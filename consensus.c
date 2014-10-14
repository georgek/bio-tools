/* makes consensus fasta file from pileup */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define TO_NEXT_TAB while (getchar() != '\t')
#define TO_NEXT_NL while (getchar() != '\n')

#define chr_l 30
static char cur_chr[chr_l+1];
static char new_chr[chr_l+1];
static int nwarns = 0, maxwarns = 10;

static inline int char2base(char c)
{
     return ((c >> 1) & 0x3);
}

static inline int numberp(char c)
{
     return c >= '0' && c <= '9';
}

static int nchars = 0;          /* number of bases printed */

void parse_chr()
{
     char c;
     int i;
     for (c = getchar(), i = 0; c != '\t' && i < chr_l; c = getchar(), ++i) {
          new_chr[i] = c;
     }
     new_chr[i] = '\0';
     if (c != '\t' && nwarns < maxwarns) {
          fprintf(stderr, "Warning, chromosome name truncated to %s.\n", new_chr);
          nwarns++;
     }
     ungetc(c, stdin);
     if (strcmp(cur_chr, new_chr) != 0){
          if (cur_chr[0] != '\0') {
               printf("\n");
          }
          strcpy(cur_chr, new_chr);
          printf(">%s\n", cur_chr);
          nchars = 0;
     }
}

int parse_number()
{
     char c;
     int number = 0;

     for (c = getchar(); numberp(c); c = getchar()) {
          number *= 10;
          number += c & 0xF;
     }
     ungetc(c, stdin);
     return number;
}

/* statics for parse_pileup_line */
static unsigned char pileup_c;
static int cur_position = 0, new_position;
static char ref_base;
static int nucs[4] = {0};
static char bases[4] = {'A','C','T','G'};
static int dels = 0;

/* just reads over indel and ignores it */
void do_indel()
{
     int length = parse_number();
     for(; length > 0; --length) {
          getchar();
     }
}

void do_del()
{
     dels++;
}

void do_quality()
{
     getchar();                 /* read over quality */
}

void do_base()
{
     nucs[char2base(pileup_c)]++;
}

void do_dot()
{
     if ('N' == ref_base && nwarns < maxwarns) {
          fprintf(stderr, "Warning: N ref base and dot\n");
     }
     else{
          nucs[char2base(ref_base)]++;
     }
}

void do_comma()
{
     if ('N' == ref_base && nwarns < maxwarns) {
          fprintf(stderr, "Warning: N ref base and comma\n");
     }
     else {
          nucs[char2base(ref_base)]++;
     }
}

void do_tab()
{
     TO_NEXT_NL;
     ungetc('\n', stdin);
}

void do_nothing()
{
     return;
}

void print_base()
{
     int i, max = nucs[0], maxidx = 0;
     for (i = 1; i < 4; i++) {
          if (nucs[i] > max){
               max = nucs[i];
               maxidx = i;
          }
     }
     if (max > 0){
          printf("%c", bases[maxidx]);
     }
     else{
          printf("N");
     }
     nchars++;
     if (nchars >= 80){
          printf("\n");
          nchars = 0;
     }
}

typedef void (*Pfun)(void);
static Pfun fun_table[8] = {do_nothing, /* 0 */
                            do_indel,   /* 1 */
                            do_del,     /* 2 */
                            do_quality, /* 3 */
                            do_base,    /* 4 */
                            do_dot,     /* 5 */
                            do_comma,   /* 6 */
                            do_tab};    /* 7 */

static unsigned char a2f[256] = {
  /* 0      1      2      3      4      5      6      7                */
  /* 8      9      A      B      C      D      E      F                */
     0,     0,     0,     0,     0,     0,     0,     0,         /* 00 */
     0,     7,     0,     0,     0,     0,     0,     0,
     0,     0,     0,     0,     0,     0,     0,     0,         /* 10 */
     0,     0,     0,     0,     0,     0,     0,     0,
     0,/* */0,/*!*/0,/*"*/0,/*#*/0,/*$*/0,/*%*/0,/*&*/0,/*'*/    /* 20 */
     0,/*(*/0,/*)*/2,/***/1,/*+*/6,/*,*/1,/*-*/5,/*.*/0,/*/*/
     0,/*0*/0,/*1*/0,/*2*/0,/*3*/0,/*4*/0,/*5*/0,/*6*/0,/*7*/    /* 30 */
     0,/*8*/0,/*9*/0,/*:*/0,/*;*/0,/*<*/0,/*=*/0,/*>*/0,/*?*/
     0,/*@*/4,/*A*/0,/*B*/4,/*C*/0,/*D*/0,/*E*/0,/*F*/4,/*G*/    /* 40 */
     0,/*H*/0,/*I*/0,/*J*/0,/*K*/0,/*L*/0,/*M*/0,/*N*/0,/*O*/
     0,/*P*/0,/*Q*/0,/*R*/0,/*S*/4,/*T*/0,/*U*/0,/*V*/0,/*W*/    /* 50 */
     0,/*X*/0,/*Y*/0,/*Z*/0,/*[*/0,/*\*/0,/*]*/3,/*^*/0,/*_*/
     0,/*`*/4,/*a*/0,/*b*/4,/*c*/0,/*d*/0,/*e*/0,/*f*/4,/*g*/    /* 60 */
     0,/*h*/0,/*i*/0,/*j*/0,/*k*/0,/*l*/0,/*m*/0,/*n*/0,/*o*/
     0,/*p*/0,/*q*/0,/*r*/0,/*s*/4,/*t*/0,/*u*/0,/*v*/0,/*w*/    /* 70 */
     0,/*x*/0,/*y*/0,/*z*/0,/*{*/0,/*|*/0,/*}*/0,/*~*/0
};

void parse_pileup_line()
{
     memset(nucs, 0, sizeof(nucs));
     dels = 0;

     parse_chr();
     TO_NEXT_TAB;
     new_position = parse_number();
     for (; cur_position < new_position - 1; cur_position++) {
          printf("N");
          nchars++;
          if (nchars >= 80) {
               printf("\n");
               nchars = 0;
          }
     }
     cur_position = new_position;
     TO_NEXT_TAB;
     ref_base = getchar();
     TO_NEXT_TAB;
     TO_NEXT_TAB;               /* number of pileups */

     /* now read main pileup to tab (qualities follow) */
     while((pileup_c = getchar()) != '\n') {
          fun_table[a2f[pileup_c]]();
     }
     print_base();
}

void parse_pileup()
{
     char nextchar;
     int nlines = 0;
     while((nextchar = getc(stdin)) != EOF) {
          nlines++;
          ungetc(nextchar, stdin);
          parse_pileup_line();
     }
}

int main(int argc, char *argv[])
{
     cur_chr[0] = '\0';
     new_chr[0] = '\0';
     parse_pileup();
     printf("\n");

     return 0;
}

