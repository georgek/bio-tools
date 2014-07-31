#include <stdlib.h>
#include <stdio.h>
#include <limits.h>
#include <ctype.h>

#include <bam/bam.h>
#include <bam/sam.h>

typedef struct pos_data {
     uint32_t tid;
     uint32_t pos;
     char base;
     samfile_t *output;
} PosData;

/* callback for bam_fetch() */
static int fetch_func(const bam1_t *b, void *data)
{
     bam_plbuf_t *buf = data;
     if (b->core.flag & BAM_FPROPER_PAIR) {
          bam_plbuf_push(b, buf);
     }
     return 0;
}

static int bambasetable[] = {-1, 'a', 'c', -1, 'g', -1, -1, -1, 't'};
/* callback for bam_plbuf_init() */
static int pileup_func_base(uint32_t tid, uint32_t pos, int n,
                            const bam_pileup1_t *pl, void *data)
{
     PosData *p = data;
     size_t i;
     int posbase;

     if (p->tid == tid && p->pos == pos) {
          for (i = 0; i < n; ++i) {
               posbase = bam1_seqi(bam1_seq(pl[i].b), pl[i].qpos);
               if (!pl[i].is_del && p->base == bambasetable[posbase]) {
                    samwrite(p->output, pl[i].b);
               }
          }
     }

     return 0;
}

static int pileup_func_del(uint32_t tid, uint32_t pos, int n,
                           const bam_pileup1_t *pl, void *data)
{
     PosData *p = data;
     size_t i;

     if (p->tid == tid && p->pos == pos) {
          for (i = 0; i < n; ++i) {
               if (pl[i].is_del) {
                    samwrite(p->output, pl[i].b);
               }
          }
     }

     return 0;
}

static int pileup_func_ins(uint32_t tid, uint32_t pos, int n,
                           const bam_pileup1_t *pl, void *data)
{
     PosData *p = data;
     size_t i;

     if (p->tid == tid && p->pos == pos) {
          for (i = 0; i < n; ++i) {
               if (pl[i].indel > 0) {
                    samwrite(p->output, pl[i].b);
               }
          }
     }

     return 0;
}

int main(int argc, char *argv[])
{
     char *progname;
     char *bamfilename;
     PosData p;
     char *outputname;

     samfile_t *bamin;
     bam_index_t *bamidx;
     bam_plbuf_t *buf;
     bam_header_t *header;

     progname = *argv;
     argv++; argc--;

     if (argc < 5) {
          printf("Usage: %s bam_file chromosome_id position base output\n",
                 progname);
          exit(-1);
     }
     else {
          bamfilename = argv[0];
          p.tid = strtoul(argv[1], NULL, 10) - 1;
          p.pos = strtoul(argv[2], NULL, 10) - 1;
          p.base = tolower(*argv[3]);
          outputname = argv[4];
     }

     /* try to open bam file */
     bamin = samopen(bamfilename, "rb", NULL);
     if (!bamin) {
          fprintf(stderr, "Error opening bamfile %s\n", bamfilename);
          exit(-1);
     }
     /* try to open index */
     bamidx = bam_index_load(bamfilename);
     if (!bamidx) {
          fprintf(stderr, "Error opening index for %s\n"
                  "(Run samtools index first)\n",
                  bamfilename);
          exit(-1);
     }
     /* try to open output */
     header = bamin->header;
     p.output = samopen(outputname, "w", header);
     if (!p.output) {
          fprintf(stderr, "Error opening output %s\n", outputname);
          exit(-1);
     }

     switch(p.base) {
     case 'i':
          buf = bam_plbuf_init(&pileup_func_ins, &p);
          break;
     case 'd':
          buf = bam_plbuf_init(&pileup_func_del, &p);
          break;
     default:
          buf = bam_plbuf_init(&pileup_func_base, &p);
          break;
     }
     /* disable maximum pileup depth */
     bam_plp_set_maxcnt(buf->iter, INT_MAX);
     bam_fetch(bamin->x.bam, bamidx,
               p.tid, p.pos, p.pos+1,
               buf, &fetch_func);
     bam_plbuf_push(0, buf);    /* finish pileup */

     bam_plbuf_destroy(buf);
     bam_index_destroy(bamidx);
     samclose(bamin);
     samclose(p.output);
     return 0;
}
