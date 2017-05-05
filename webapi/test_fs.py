import sys
import os

def get_open_fds(pid):
    '''
    return the number of open file descriptors for current process

    .. warning: will only work on UNIX-like os-es.
    '''
    import subprocess
    import os

    #pid = os.getpid()
    procs = subprocess.check_output(
        [ "lsof", '-w', '-Ff', "-p", str( pid ) ] )

    nprocs = len(
        filter(
            lambda s: s and s[ 0 ] == 'f' and s[1: ].isdigit(),
            procs.split( '\n' ) )
        )
    return nprocs

if __name__ == "__main__":
    import sys

    if len (sys.argv) > 1:
        myid = int(sys.argv[1])
    else:
        print (" ID missing ...")
        sys.exit(0)

    x = get_open_fds(myid)
    print ( x )


