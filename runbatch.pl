#!/usr/bin/perl
#use File::Copy;
#use File::Basename;
use Cwd;
use File::Basename qw(dirname);
use Cwd qw(abs_path);
use lib dirname(abs_path($0)) . '/lib';
use Icg::Runner qw(runSimulation);

sub listFiles{
    local (@files, @tmpfiles);
    opendir(DIR,$_[0]) || die("Error: Cannot open directory $_[0] \n");
    @tmpfiles = readdir(DIR);
    closedir(DIR);
    
    foreach $file (@tmpfiles){
          if( (($file eq ".") || ($file eq "..") || substr($file, 0, 1 ) eq ".")) {
    } else {
     push( @files, $file);
        }
     }
    return @files;
}

if (@ARGV < 3) {
   print "Usage: ./runbatch <inputdir> <configFile> <resultdir>\n"; 
   exit;
}

$inputDir      = $ARGV[0];
$configFile    = $ARGV[1];
$resultDir     = $ARGV[2];
print "\nDirectory to process: $inputDir\n";
@files = listFiles($inputDir);
system("mkdir $resultDir");

$mydir = getcwd;
$scriptBaseDir = dirname(abs_path($0));
$ENV{LD_LIBRARY_PATH} .= $mydir;

foreach $file  (@files){
    print "processing... $dir/$file \n";
    runSimulation("$inputDir/$dir/$file", $configFile, $resultDir, $scriptBaseDir); 
    #system("chgrp -R lcn1 $resultDir");
    system("chmod -R g+w $resultDir");
    system("rm -rf   /lcncluster/vogels/ngene/simulation/nrn/x86_64 ");
}
