#!/usr/bin/perl
package Icg::Runner;
use strict;
use warnings;
use Exporter qw(import);
our @EXPORT_OK = qw(runSimulation);

use File::Copy;
use File::Basename;
use Cwd;

#inputs 
#1. modfile name
#2. configFile
#2. resultdir
sub runSimulation{

	my ($this,$cmdStr, @list, @f, $Suffix, $traceFile, $featureFile, $bn, $dn, $en, $mydir, $custom_code_name, $custom_mod_name);
    my ($modFile,$configFile,$resultDir,$scriptBaseDir) = @_;
    
    system("cp $modFile tmpmod.mod");
    system("rm -rf x86_64"); system("rm -rf i386");
    #copy("fel.mod", "tmp/");
    $mydir = getcwd;
    #system("nrnivmodl -loadflags \'-L$mydir  -lFeature\'");
    
    print "\nCompiling NEURON code:\n--------------------\n";
    my $exit_code = system("nrnivmodl -loadflags \'-L$mydir \'");
    print "EXIT CODE $exit_code";
    if($exit_code!=0)
    {
      print "--------------------\nCompilation failed with exit code $exit_code.\n";
      exit($exit_code >> 8);
    }
    else
    {
      print "--------------------\nCompilation successful!\n";
    }

    open(F,"tmpmod.mod");
    @list=<F>;close F;
    $this = "SUFFIX";
    @f=grep /$this/,@list;
    @f = split(' ', $f[0]);
    $Suffix = $f[1];
    print "\nSuffix : $f[1] ";
    ($bn, $dn, $en) = fileparse($modFile, ('\.mod'));
    $traceFile = $resultDir . "/" . $bn ;
    $featureFile = $resultDir . "/" . $bn ;
    $cmdStr = sprintf("load_file(\"nrngui.hoc\")\n strdef suffix, confFile, traceFile, featureFile \n suffix      = \"%s\"\n confFile    = \"%s\" \n traceFile   =\"%s\"\n featureFile = \"%s\" \n\n", $Suffix, $configFile, $traceFile, $featureFile);
    print "\ncommand is $cmdStr";
    open(HEADER, ">head.hoc");
    print HEADER "$cmdStr";
    close(HEADER);

    # check if the protocol is kca. if so, choose different template file
    if ($configFile eq "kcaconfig.in") {
        print "Using KCA template file...\n";
        system("cat head.hoc $scriptBaseDir/template_kca.hoc > tmp.hoc");
    } else{
        print "Using standard template file...\n";
        system("cat head.hoc $scriptBaseDir/template.hoc > tmp.hoc");
    }

    # add extra code and file dependencies for this file:
    system("rm customcode.hoc");
    system("touch customcode.hoc");
    print "\nLooking for custom code '$bn': ";
    $custom_code_name = "icg-channels-customcode/customcode_" . $bn . ".hoc";
    if (-e $custom_code_name) {
        print "Copying custom code file in: $custom_code_name\n";
        system("cp $custom_code_name customcode.hoc");
    } else {
        print "No custom code files exist.\n";
    }

    # copy dependent files if this is called from a different directory
    if ($mydir ne $scriptBaseDir) {
        print "Copying dependency files to working directory\n";
        my @names = ("map.hoc","vcCell.hoc","grph.hoc","configReader1.hoc","APwaveform.dat");
        foreach my $name (@names)
        {
            print ("$name\n");
            system("cp $scriptBaseDir/$name $mydir");
        }
        system("cp $configFile $mydir")
    }

    #$custom_mod_name = "custom_code/mod_files/" . $bn . "*";
    #print "$custom_mod_name\n";
    #system("cp $custom_mod_name . ");
    print "\nRunning NEURON protocols:\n--------------------\n";
    $exit_code = system ("nrngui tmp.hoc");
    print "EXIT CODE $exit_code";
    if($exit_code!=0)
    {
      print "--------------------\nrun failed with exit code $exit_code.\n";
      exit($exit_code >> 8);
    }
    else
    {
      print "--------------------\nrun was successful!\n";
    }

    # my $out = `nrnivmodl -loadflags \'-L$mydir \' 2>&1`;
    # print $out;
    # if($out =~ m/Error 1/ or $out =~ m/syntax error/) {
    #     print "--------------------\nCompilation failed.\n";
    #     exit(1);
    # }
    # else
    # {
    #   print "--------------------\nCompilation successful!\n";
    # }

    # remove all mod files from this directory
    # - includes tmpmod.mod and other files that may have been copied in customcode
    # this is a bit dangerous, but i can't think of another easy solution
    #system("rm *.mod");	 
}
