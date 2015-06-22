#!/usr/bin/perl
#use File::Copy;
#use File::Basename;
use Cwd;
use File::Basename qw(dirname);
use Cwd qw(abs_path);
use lib dirname(abs_path($0)) . '/lib';
use Icg::Runner qw(runSimulation);

if (@ARGV < 3) {
   print "Usage: ./runbatch <inputfile> <configFile> <resultdir>\n"; 
   exit;
}

$inputFile      = $ARGV[0];
$configFile    = $ARGV[1];
$resultDir     = $ARGV[2];
print "\nFile to process: $inputFile\n";
system("mkdir $resultDir");
$mydir = getcwd;
$scriptBaseDir = dirname(abs_path($0));

# Add custom code directory to working dir
system("ln -s $scriptBaseDir/custom_code custom_code");

$ENV{LD_LIBRARY_PATH} .= $mydir;

print "processing... $inputFile \n";
runSimulation("$inputFile", $configFile, $resultDir, $scriptBaseDir); 
system("chmod -R g+w $resultDir");