#include <stdlib.h>
#include <stdio.h>
#include <memory.h>
#include <ctype.h>
#include <assert.h>

#define FLANK_LEN 60
#define ARR_INIT_SIZE 8

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

void buffer_to_string(struct buffer *buf, char *string)
{
     assert(string != NULL);
     memcpy(string,
            buf->items + buf->beg,
            buf->size - buf->beg);
     memcpy(string + buf->size - buf->beg,
            buf->items,
            buf->beg);
}

/* struct for holding an output */
typedef struct output
{
     char *string;  /* the complete output string */
     int num_n;     /* number of Ns following this string */
     int seen;      /* has this or the mate been seen? */
     struct output *mate; /* the reverse complement of this */
} Output;

Output *new_output(int strlen, struct output *mate)
{
     struct output *new = malloc(sizeof(struct output));
     new->string = malloc(strlen+1);
     new->string[strlen] = '\0';
     new->seen = 0;
     new->mate = mate;
     return new;
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
     char *string;
     Output *output;
     struct node *next[4];
} Node;

typedef struct node_array
{
     int length;
     int max_length;
     Node **states;
} NodeArray;

Node *new_Node(int state)
{
     Node *new = malloc(sizeof(struct node));
     new->state = state;
     new->string = NULL;
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
     array.max_length = ARR_INIT_SIZE;
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
     current->string = string;
}

void go_add_Output(NodeArray *go, Output *output)
{
     int i, basei;
     Node *root, *current;
     root = go->states[0];

     for (current = root, i = 0; output->string[i] != '\0'; ++i) {
          basei = b2i(output->string[i]);
          if (current->next[basei] == NULL) {
               current->next[basei] = new_Node(go->length);
               add_Node(go, current->next[basei]);
          }
          current = current->next[basei];
     }
     current->output = output;
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
                         strlen(go->states[s]->output->string) :
                         0;
                    nol = go->states[t]->next[i]->output ?
                         strlen(go->states[t]->next[i]->output->string) :
                         0;
                    if (nol > ol) {
                         go->states[s]->output->string =
                              go->states[t]->next[i]->output->string;
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
          if (current->string != NULL) {
               printf("%d, %s\n", i, current->string);
          }
     }
}

void search_all_in_file(FILE *fasta, NodeArray *go, int *failures)
{
     int i = 1, c, skip = 0, basei;
     Node *current = go->states[0];

     while ((c = getc(fasta)) != EOF) {
          if (c == '\n' && skip) {
               i++;
               skip = 0;
          }
          else if (skip) {
               continue;
          }
          else if (c == '>') {
               current = go->states[0];
               skip = 1;
          }
          else switch (toupper(c)) {
               case 'A':
               case 'C':
               case 'G':
               case 'T':
                    basei = b2i(c);
                    while (current->next[basei] == NULL) {
                         current = go->states[failures[current->state]];
                    }
                    if (current->next[basei] != NULL) {
                         current = current->next[basei];
                    }
                    if (current->output != NULL) {
                         printf("%d, %s\n", i, current->output->string);
                    }
                    break;
               case '\n':
                    i++;
                    break;
               }
     }
}

void put_flanks_in_go(NodeArray *go, FILE *fasta, int flank_len)
{
     int c, skip = 0;
     struct buffer ring_buf;
     Output *fwd_output, *rev_output;

     init_buffer(&ring_buf, flank_len);

     while ((c = getc(fasta)) != EOF) {
          if (c == '\n' && skip) {
               skip = 0;
          }
          else if (skip) {
               continue;
          }
          else if (c == '>') {
               buffer_clear(&ring_buf);
               skip = 1;
          }
          else switch (toupper(c)) {
               case 'N':
                    fwd_output = new_output(flank_len, NULL);
                    buffer_to_string(&ring_buf, fwd_output->string);
                    buffer_clear(&ring_buf);
                    printf("%s\n", fwd_output->string);
                    go_add_Output(go, fwd_output);
                    while (toupper(c = getc(fasta)) == 'N' || c == '\n');
               case 'A':
               case 'C':
               case 'G':
               case 'T':
                    buffer_put(&ring_buf, c);
                    break;
               }
     }

     free_buffer(&ring_buf);
}

int main(int argc, char *argv[])
{
     NodeArray go = init_go();
     int *failures;

     FILE *contigs, *scaffolds;

     if (argc < 3) {
          printf("usage: %s contigs scaffolds\n", argv[0]);
          return 1;
     }

     contigs = fopen(argv[1], "r");
     if (contigs) {
          put_flanks_in_go(&go, contigs, FLANK_LEN);
     }
     finish_go(&go);

     failures = build_failures(&go);
     
     scaffolds = fopen(argv[2], "r");
     if (scaffolds) {
          search_all_in_file(scaffolds, &go, failures);
     }

     return 0;
}
