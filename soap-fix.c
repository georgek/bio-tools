#include <stdlib.h>
#include <stdio.h>
#include <memory.h>
#include <ctype.h>

/* Quick Search */

/* Modified implementation from:
 * http://www-igm.univ-mlv.fr/~lecroq/string/node19.html
 * by Christian Charras and Thierry Lecroq
 *
 * Algorithm from:
 * Hume, Andrew, and Daniel Sunday. "Fast string searching."
 * Software: Practice and Experience 21, no. 11 (1991): 1221-1248.*/

#define FLANK_LEN 60

/* a ring buffer */
struct buffer
{
     size_t beg, size;
     char *items;
};

int init_buffer(struct buffer *buf, size_t size)
{
     buf->beg = 0;
     buf->size = size;
     buf->items = calloc(size, sizeof(char));
     if (!buf->items) {
          return -1;
     }
     return 0;
}

void free_buffer(struct buffer *buf)
{
     buf->beg = 0;
     buf->size = 0;
     free(buf->items);
}

void buffer_put(struct buffer *buf, char item)
{
     *(buf->items + buf->beg) = item;
     buf->beg = (buf->beg + 1)%buf->size;
}

char buffer_get(struct buffer *buf)
{
     char last = *(buf->items + buf->beg);
     *(buf->items + buf->beg) = 0;
     buf->beg = (buf->beg + 1)%buf->size;
     return last;
}

void buffer_clear(struct buffer *buf)
{
     while (*(buf->items + buf->beg) != 0) {
          *(buf->items + buf->beg) = 0;
          buf->beg = (buf->beg + 1)%buf->size;
     }
}

void buffer_skip_nulls(struct buffer *buf)
{
     while (*(buf->items + buf->beg) == 0) {
          buf->beg = (buf->beg + 1)%buf->size;
     }
}

#define ASIZE 256

void preQsBc(unsigned char *s, int slen, int qsBc[])
{
     int i;

     for (i = 0; i < ASIZE; ++i) {
          qsBc[i] = slen + 1;
     }
     for (i = 0; i < slen; ++i) {
          qsBc[s[i]] = slen - i;
     }
}

int QS(unsigned char *sch, int slen, unsigned char *txt, int tlen)
{
     int j, qsBc[ASIZE];

     /* Preprocessing */
     preQsBc(sch, slen, qsBc);

     /* Searching */
     j = 0;
     while (j <= tlen - slen) {
          if (memcmp(sch, txt+j, slen) == 0) {
               return j;
          }
          j += qsBc[txt[j + slen]];  /* shift */
     }
     return -1;
}

/* Aho-Corasick algorithm for multiple string/dictionary search */

/* this implementation only supports characters ACGT (case insensitive) */

/* this lets us quickly use bases as indexes, ACTG = 0123, upper or lower */
enum base {A,C,T,G};
int b2i(char c)
{
     return (c >> 1) & 0x3;
}

typedef struct node
{
     int state;
     char *output;
     struct node *next[4];
} Node;

typedef struct node_array
{
     int length;
     int max_length;
     Node **states;
} NodeArray;

#define INIT_SIZE 8
Node *new_Node(int state)
{
     Node *new = malloc(sizeof(struct node));
     new->state = state;
     new->output = NULL;
     new->next[A] = NULL;
     new->next[C] = NULL;
     new->next[G] = NULL;
     new->next[T] = NULL;
     return new;
}

NodeArray new_NodeArray()
{
     NodeArray array;
     array.length = 0;
     array.max_length = INIT_SIZE;
     array.states = malloc(sizeof(array.states) * array.max_length);
     return array;
}

void add_Node(NodeArray *array, Node *new)
{
     if (array->length >= array->max_length) {
          array->max_length <<= 1;
          array->states = realloc(array->states,
                                  sizeof(array->states) * array->max_length);
     }
     array->states[array->length++] = new;
}

NodeArray init_go()
{
     NodeArray nodes = new_NodeArray();
     Node *root = new_Node(0);
     add_Node(&nodes, root);
     return nodes;
}

void finish_go(NodeArray *go)
{
     int i;
     Node *root = go->states[0];
     for (i = 0; i < 4; ++i) {
          if (root->next[i] == NULL) {
               root->next[i] = root;
          }
     }
}

void go_add_string(NodeArray *go, char *string)
{
     int i, basei;
     Node *root, *current;
     root = go->states[0];

     for (current = root, i = 0; string[i] != '\0'; ++i) {
          basei = b2i(string[i]);
          if (current->next[basei] == NULL) {
               current->next[basei] = new_Node(go->length);
               add_Node(go, current->next[basei]);
          }
          current = current->next[basei];
     }
     current->output = string;
}

NodeArray build_go(char **strings, int n)
{
     int i;
     NodeArray go = init_go();

     for (i = 0; i < n; ++i) {
          go_add_string(&go, strings[i]);
     }

     finish_go(&go);

     return go;
}

int *build_failures(NodeArray *go)
{
     int *failures = malloc(sizeof(int) * go->length);
     int *queue = malloc(sizeof(int) * go->length);
     int *start = queue, *end = queue, *current;
     int i, s, t;
     int ol, nol;

     for (i = 0; i < 4; ++i) {
          if (go->states[0]->next[i] != go->states[0]) {
               s = go->states[0]->next[i]->state;
               *(end++) = s;
               failures[s] = 0;
          }
     }
     while (start != end) {
          current = start++;
          for (i = 0; i < 4; ++i) {
               if (go->states[*current]->next[i] != NULL) {
                    s = go->states[*current]->next[i]->state;
                    *(end++) = s;
                    t = failures[*current];
                    while (go->states[t]->next[i] == NULL) {
                         t = failures[t];
                    }
                    failures[s] = go->states[t]->next[i]->state;
                    ol = go->states[s]->output ?
                         strlen(go->states[s]->output) :
                         0;
                    nol = go->states[t]->next[i]->output ?
                         strlen(go->states[t]->next[i]->output) :
                         0;
                    if (nol > ol) {
                         go->states[s]->output =
                              go->states[t]->next[i]->output;
                    }
               }
          }
     }

     free(queue);
     return failures;
}

void search_all(char *text, int len, NodeArray go, int *failures)
{
     int i, basei;
     Node *current;

     for (i = 0, current = go.states[0]; i < len; ++i) {
          if (text[i] == '\n') {
               continue;
          }
          basei = b2i(text[i]);
          while (current->next[basei] == NULL) {
               current = go.states[failures[current->state]];
          }
          if (current->next[basei] != NULL) {
               current = current->next[basei];
          }
          if (current->output != NULL) {
               printf("%d, %s\n", i, current->output);
          }
     }
}

void put_flanks_in_go(NodeArray *go, FILE *fasta, int flank_len)
{
     int c, skip = 0;
     char b;
     struct buffer buf;

     init_buffer(&buf, flank_len);

     while ((c = getc(fasta)) != EOF) {
          if (c == '\n' && skip) {
               skip = 0;
          }
          else if (skip) {
               continue;
          }
          else if (c == '>') {
               buffer_clear(&buf);
               skip = 1;
          }
          else if (toupper(c) == 'N') {
               buffer_skip_nulls(&buf);
               while ((b = buffer_get(&buf)) != 0){
                    putchar(b);
               }
               printf("\n");
               while (toupper(c = getc(fasta)) == 'N');
               buffer_put(&buf, c);
          }
          else {
               buffer_put(&buf, c);
          }
     }

     free_buffer(&buf);
}

int main(int argc, char *argv[])
{
     /* int res; */
     /* int pos = 0; */

     /* unsigned char text[] = "ifoisjfoejfoiewj"; */
     /* unsigned char search[] = "foi"; */
     /* int tlen = sizeof(text) - 1; */
     /* int slen = sizeof(search) - 1; */

     /* char new_text[] = "ggatcgatgagatatcgcgctagctagtgagctcgcgctaaagctcgatacgggatcgatcgatcgcgagatcgcgggag"; */
     /* char *strings[] = {"cgtagctga", "cgtagctagg", "acgtagct", "aagctcgat", "ctcgatacgg", "cgtaggctag"}; */

     NodeArray go;
     int *failures;

     FILE *fasta;

     /* exhaustive search */
     /* while (pos <= tlen - slen) { */
     /*      res = QS(search, slen, text + pos, tlen - pos); */
     /*      if (res < 0) { */
     /*           break; */
     /*      } */
     /*      printf("%d\n", pos + res); */
     /*      pos += res + slen; */
     /* } */

     /* go = build_go(strings, 6); */


     fasta = fopen(argv[1], "r");
     if (fasta) {
          put_flanks_in_go(&go, fasta, FLANK_LEN);
     }
     
     /* failures = build_failures(&go); */

     /* printf("%d\n", go.length); */
     /* for (pos = 0; pos < go.length; ++pos) { */
     /*      printf("this state: %d\n", go.states[pos]->state); */
     /*      if (go.states[pos]->output) { */
     /*           printf("output: %s\n", go.states[pos]->output); */
     /*      } */
     /*      else { */
     /*           printf("output: %s\n", "none"); */
     /*      } */
     /*      if (go.states[pos]->next[A]) { */
     /*           printf("next state A: %d\n", go.states[pos]->next[A]->state); */
     /*      } */
     /* } */

     /* printf("%s\n", new_text); */
     /* search_all(new_text, sizeof(new_text), go, failures); */

     return 0;
}
