#include <stdlib.h>
#include <stdio.h>
#include <limits.h>

#include <getopt.h>

#include <bam/bam.h>
#include <bam/sam.h>

/* callback for bam_fetch() */
static int fetch_func(const bam1_t *b, void *data)
{
     bam_plbuf_t *buf = data;
     if (b->core.flag & BAM_FPROPER_PAIR) {
          bam_plbuf_push(b, buf);
     }
     return 0;
}

/* callback for bam_plbuf_init() */
static int pileup_func(uint32_t tid, uint32_t pos, int n,
                       const bam_pileup1_t *pl, void *data)
{
     uint32_t *next_pos = data;
     while (*next_pos < pos) {
          printf("%u\t0\n", *next_pos);
          (*next_pos)++;
     }
     printf("%u\t%d\n", pos, n);
     *next_pos = pos+1;
     return 0;
}

int main(int argc, char *argv[])
{
     char *progname;

     char *bamfilename;
     int32_t tid;

     samfile_t *bamin;
     bam_index_t *bamidx;
     bam_plbuf_t *buf;
     bam1_t *bam_read;
     uint32_t next_pos = 1;

     progname = *argv;
     argv++; argc--;
     if (argc < 2) {
          printf("Usage: %s bam_file tid\n", progname);
          exit(1);
     }
     else {
          bamfilename = argv[0];
          tid = strtol(argv[1], NULL, 10);
     }

     /* try to open bam file */
     bamin = samopen(bamfilename, "rb", NULL);
     if (!bamin) {
          fprintf(stderr, "Error opening bamfile %s\n", bamfilename);
          exit(1);
     }
     /* try to open index */
     bamidx = bam_index_load(bamfilename);
     if (!bamidx) {
          fprintf(stderr, "Error opening index for %s\n", bamfilename);
          exit(1);
     }
     bam_read = bam_init1();

     buf = bam_plbuf_init(&pileup_func, &next_pos);
     /* disable maximum pileup depth */
     bam_plp_set_maxcnt(buf->iter, INT_MAX);
     bam_fetch(bamin->x.bam, bamidx,
               tid, 0, INT_MAX,
               buf, &fetch_func);
     bam_plbuf_push(0, buf);    /* finish pileup */

     bam_plbuf_destroy(buf);
     bam_destroy1(bam_read);
     bam_index_destroy(bamidx);
     samclose(bamin);
     return 0;
}
