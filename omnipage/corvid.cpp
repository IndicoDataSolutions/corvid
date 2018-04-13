#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <limits.h>
#include <errno.h>
#include <libgen.h>
#include <string.h>

#include "KernelApi.h"
#include "RecApiPlus.h"

using namespace std;

#define SID 0

int main (int argc, char *argv[])
{
    char opt;
    char *strInput = (char *) malloc (PATH_MAX);
    char *strOutput = (char *) malloc (PATH_MAX);
    char *strFormat = (char *) malloc (PATH_MAX);
    char *strOutputLevel = (char *) malloc (PATH_MAX);

    while ((opt = (char) (getopt (argc, argv, "Ri:o:f:l:"))) != EOF)
    {
        switch (opt)
        {
              case 'i':
                  realpath (optarg, strInput);
                  break;
              case 'o':
                  realpath (optarg, strOutput);
                  break;
              case 'f':
                  strFormat = optarg;
                  break;
              case 'l':
                  strOutputLevel = optarg;
                  break;
              default:
                  printf("Use -i filenamein -o filenameout -f outputformat -l outputlevel; do not use STDIO\n");
                  exit (1);
        }
    }
    LPCSTR inputFiles[2];
    inputFiles[0] = strInput;
    inputFiles[1] = NULL;
    RECERR rc;
    
    rc = RecInitPlus(NULL, NULL);    
    //Use 3-way voting engine
    rc = kRecSetDefaultRecognitionModule(0, RM_OMNIFONT_PLUS3W);


    printf("XML output\n");
    kRecSetDTXTFormat(0, DTXT_XMLCOORD);


    kRecProcessPages(0, strOutput, inputFiles, NULL, NULL, NULL);
    if(rc != REC_OK)
    {    
        //Handle errors (add similar code elsewhere as needed)
        printf("Error Processing: %X\n", rc);
        return 1;
    }    

    RecQuitPlus();
    return 0;
}



