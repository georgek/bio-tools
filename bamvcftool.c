/* Takes a BAM file and VCF file and returns SAM file containing all reads
 * containing one or more of the variants */

#include <stdlib.h>
#include <stdio.h>
#include <limits.h>

#include <bam.h>

#include <htslib/vcf.h>
#include <htslib/sam.h>

struct pos_data {
     uint32_t tid;
     uint32_t pos;
     char base;
     bam_hdr_t *header;
     samFile *output;
};

/* callback for bam_fetch() */
static int fetch_func(const bam1_t *b, void *data)
{
     bam_plbuf_t *buf = data;
     bam_plbuf_push(b, buf);
     return 0;
}

static int bambasetable[] = {-1, 'a', 'c', -1, 'g', -1, -1, -1, 't'};
/* callback for bam_plbuf_init() */
static int pileup_func(uint32_t tid, uint32_t pos, int n,
                       const bam_pileup1_t *pl, void *data)
{
     struct pos_data *p = data;
     size_t i;
     int posbase;

     if (p->tid == tid && p->pos == pos) {
          for (i = 0; i < n; ++i) {
               posbase = bam1_seqi(bam1_seq(pl[i].b), pl[i].qpos);
               if (!pl[i].is_del && p->base == bambasetable[posbase]) {
                    sam_write1(p->output, p->header, pl[i].b);
               }
          }
     }

     return 0;
}

int main(int argc, char *argv[])
{
     char *progname;
     char *bamfilename, *vcffilename, *outputname;

     vcfFile *vcfin;
     bcf_hdr_t *vcfheader;
     bcf1_t vcfread;

     samFile *bamin;
     hts_idx_t *bamidx;
     /* bam_plbuf_t *buf; */
     bam1_t bamread;
     bam_plbuf_t *buf;

     struct pos_data p;

     memset(&vcfread, 0, sizeof(vcfread));
     memset(&bamread, 0, sizeof(bamread));

     progname = *argv;
     argv++; argc--;

     if (argc < 3) {
          printf("Usage: %s vcf_file bam_file output\n",
                 progname);
          exit(-1);
     }
     else {
          vcffilename = argv[0];
          bamfilename = argv[1];
          outputname = argv[2];
     }
     p.tid = 0;
     p.pos = 0;
     p.base = 'a';

     /* try to open vcf file */
     vcfin = vcf_open(vcffilename, "r");
     if (!vcfin) {
          fprintf(stderr, "Error opening vcf file %s\n", vcffilename);
          exit(-1);
     }
     vcfheader = vcf_hdr_read(vcfin);
     /* try to open bam file */
     bamin = hts_open(bamfilename, "rb");
     if (!bamin) {
          fprintf(stderr, "Error opening bam file %s\n", bamfilename);
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
     p.header = bam_hdr_read(bamin->fp.bgzf);
     p.output = hts_open(outputname, "w");
     if (!p.output) {
          fprintf(stderr, "Error opening output %s\n", outputname);
          exit(-1);
     }
     sam_hdr_write(p.output, p.header);

     while (bcf_read(vcfin, vcfheader, &vcfread) >= 0) {
          printf("chr: %d, pos: %d, len: %d, qual: %f\n",
                 vcfread.rid, vcfread.pos, vcfread.rlen, vcfread.qual);
          printf("n_info: %u, n_allele: %u, n_fmt: %u, n_sample: %u\n",
                 vcfread.n_info, vcfread.n_allele,
                 vcfread.n_fmt, vcfread.n_sample);
          bcf_unpack(&vcfread, BCF_UN_STR);
          printf("ref: %s\n", vcfread.d.allele[0]);
          for (int i = 1; i < vcfread.n_allele; i++) {
               printf("var: %s\n", vcfread.d.allele[i]);
          }
          bcf_get_variant_types(&vcfread);
          for (int i = 1; i < vcfread.n_allele; i++) {
               switch (vcfread.d.var[i].type) {
               case VCF_REF:
                    printf("%d ref ", i);
                    break;
               case VCF_SNP:
                    printf("%d snp ", i);
                    break;
               case VCF_MNP:
                    printf("%d mnp ", i);
                    break;
               case VCF_INDEL:
                    printf("%d indel ", i);
                    break;
               case VCF_OTHER:
                    printf("%d other ", i);
                    break;
               default:
                    printf("%d unrec (%d) ", i,
                           bcf_get_variant_type(&vcfread, i));
               }
               printf("bases: %d\n", vcfread.d.var[i].n);
          }
          printf("\n");
     }

     buf = bam_plbuf_init(&pileup_func, &p);
     bam_plp_set_maxcnt(buf->iter, INT_MAX);
     bam_fetch(bamin->fp.bgzf, bamidx,
               p.tid, p.pos, p.pos + 1,
               buf, &fetch_func);
     bam_plbuf_push(NULL, buf);    /* finish pileup */

     bam_plbuf_destroy(buf);
     sam_close(p.output);
     bam_hdr_destroy(p.header);
     hts_idx_destroy(bamidx);
     sam_close(bamin);
     bcf_hdr_destroy(vcfheader);
     vcf_close(vcfin);

     return 0;
}

