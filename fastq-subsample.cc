#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>
#include <random>

int main(int argc, char *argv[])
{
    double divide_coverage;
    int old_read_length;
    int new_read_length;
    double len_ratio;
    double cov_ratio;
    int random_seed;

    std::ios_base::sync_with_stdio(false);

    if (argc < 4
        || argc > 1
           && (strcmp(argv[1], "-h") == 0
               || strcmp(argv[1], "--help") == 0)) {
        std::cerr
            << "usage: " << argv[0] << " [-h]"
            " divide_coverage old_read_length new_read_length [random_seed]\n"
            "    Reads fastq and from standard input and prints subsampled\n"
            "    version to standard output. Coverage is divided by\n"
            "    divide_coverage."
            << std::endl;
        std::exit(0);
    }
    divide_coverage = std::stod(argv[1]);
    old_read_length = std::stoi(argv[2]);
    new_read_length = std::stoi(argv[3]);
    len_ratio = new_read_length/(double) old_read_length;
    cov_ratio = 1.0/divide_coverage/len_ratio;

    std::mt19937 mt;
    if (argc > 4) {
        random_seed = std::stod(argv[4]);
        mt = std::mt19937(random_seed);
    }
    else {
        std::random_device rd;
        mt = std::mt19937(rd());
    }
    std::uniform_real_distribution<double> uniform(0,1);

    int n = 0;
    std::string lines[4];
    while (std::cin) {
        std::getline(std::cin, lines[n++]);
        if (n > 3) {
            n = 0;
            if (uniform(mt) < cov_ratio) {
                std::cout << lines[0] << "\n";
                std::cout << lines[1].substr(0,new_read_length) << "\n";
                std::cout << lines[2] << "\n";
                std::cout << lines[3].substr(0,new_read_length) << "\n";
            }
        }
    }
}
