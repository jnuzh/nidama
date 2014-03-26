<?php
    
    /**
     * @author  Michael Heim
     * @link    http://www.zeilenwechsel.de/
     * @version 1.2.0
     * @license http://www.zeilenwechsel.de/it/code/browse/komodo-phpunit-harness/prod/license.txt
     */
    
    require_once( dirname( dirname( __file__ ) ) . '/Utils/Loader.php' );
    PHPUnitXt_Utils_Loader::load( 'PHPUnitXt_Base_Command' );
    PHPUnitXt_Utils_Loader::load( 'PHPUnitXt_Ko_Printer' );
    
    
    /**
     * A PHPUnit test runner for the command line, modified for Komodo. Supports additional output options.
     */
    class PHPUnitXt_Ko_Command extends PHPUnitXt_Base_Command {
        
        /**
         * Alternative to main(), allowing to pass in command line arguments and default options.
         *
         * @param array                         $args                an array corresponding to $_SERVER['argv']
         * @param PHPUnitXt_Base_PrinterOptions $printer_defaults
         * @param array                         $blacklist           paths to be removed from stack trace; for use with PHPUnit 3.6
         * @param bool                          $exit
         * @return void
         */
        public static function exec ( array $args, PHPUnitXt_Base_PrinterOptions $printer_defaults = null, array $blacklist = array(), $exit = true ) {
            
            self::configure_and_run( new PHPUnitXt_Ko_Command(), $args, new PHPUnitXt_Ko_Printer(), $printer_defaults, $blacklist, $exit );
            
        }
        
        /**
         * Configures and runs a PHPUnitXt_Ko_Command class. Extracted from exec() for testability.
         * 
         * @param PHPUnitXt_Ko_Command            $command            a PHPUnitXt_Ko_Command instance
         * @param array                           $args               the arguments as stored in the $_SERVER array
         * @param PHPUnitXt_Base_Printer          $printer            a result printer instance
         * @param PHPUnitXt_Base_PrinterOptions   $printer_defaults
         * @param array                           $blacklist          paths to be removed from stack trace; for use with PHPUnit 3.6
         * @param boolean                         $exit
         * 
         * @return void
         */
        public static function configure_and_run ( PHPUnitXt_Ko_Command $command, array $args, PHPUnitXt_Base_Printer $printer, PHPUnitXt_Base_PrinterOptions $printer_defaults = null, array $blacklist = array(), $exit = true ) {
            
            $exit = ( $exit and ! self::suppress_termination() );
            
            $command->set_printer( $printer, $printer_defaults, $blacklist )
                    ->register_fatal_error_handler();
            
            $args = self::reorder_args( $args );    // added for Komodo
            $args = $command->fix_path( $args );    // added for Komodo
            
            $command->run( $args, false );
            $command->has_run_all_tests();
            
            if ( $exit ) exit();
            
        }
        
        /**
         * Reshuffling arguments. Komodo provides the path to the test directory as the
         * second argument. PHPUnit expects it as the last one.
         *
         * NB: The directory might have to be removed from the arguments altogether if
         * the user has specified a test name, filepath, directory or XML config file.
         * This is handled separately in fix_path.
         * 
         * @param  array   $args
         * @return array
         */
        protected static function reorder_args( array $args ) {
            
            $ko_runner = array_shift( $args );  // the filepath of Komodo's drive_testrunner.php
            $args[] = array_shift( $args );     // the path to the test dir or file - must be moved to the end
            array_unshift( $args, $ko_runner ) ;
            
            return $args;
            
        }
        
        /**
         * Removes the test directory added by Komodo if it conflicts with the arguments
         * provided by the user. Sets the working directory as needed.
         * 
         * @param  array   $args
         * @return array
         */
        protected function fix_path ( array $args ) {
            
            $args_orig = $args;
            
            // Separate the test directory defined in the Komodo interface from the user arguments.
            $ko_testdir = array_pop( $args );
            
            if ( $this->user_has_defined_specific_tests( $args ) or $this->is_using_xml_config( $args, $ko_testdir ) ) {
                
                // The user has specified additional path information in the arguments
                // or an XML config file. In order to avoid conflicts,
                // (1) set the working directory to the directory defined in the Komodo
                //     interface ($ko_testdir)
                // (2) keep that directory removed from the arguments (already done)
                // (3) pass on any user-provided path information as standard PHPUnit
                //     CLI arguments (no action required).
                $this->set_working_dir( $ko_testdir );
                
            } else {
                
                // No additional path information specified. Use the original, unaltered arguments.
                $args = $args_orig;
                
            }
            
            return $args;
            
        }
        
        /**
         * Returns if the arguments contain a test name, file path or directory path
         * explicitly specified by the user as a PHPUnit command line option.
         * 
         * Expects an array of PHPUnit command line arguments (including those
         * belonging to the Komodo test harness extension, such as '--in-groups').
         * Arguments added by Komodo, ie the test runner path and the test directory,
         * must be removed beforehand.
         *
         * @param  array $user_args
         * @return boolean
         */
        protected function user_has_defined_specific_tests ( array $user_args ) {
            
            // Let PHPUnit analyze the arguments.
            try {
                
                $options = PHPUnit_Util_Getopt::getopt( $user_args, 'd:c:', array_keys( $this->longOptions ) );
                
            } catch (RuntimeException $e) {
                
                PHPUnit_TextUI_TestRunner::showError( $e->getMessage() );
                
            }
            
            // $options[1] contains an array of arguments which are not associated with
            // a switch. Arguments of this kind are either a test name, a test file path
            // or a test directory.
            $has_test_or_path_info = ( count( $options[1] ) != 0 );
            
            return $has_test_or_path_info;
            
        }
        
        /**
         * Checks if an XML configuration file is used.
         *
         * That is the case if
         * - the arguments specify an XML configuration file
         * - the default XML config file (phpunit.xml or phpunit.xml.dist) is present
         *   in the test directory as defined in the Komodo UI.
         *
         * But the default XML config will duly be ignored if the --no-configuration
         * switch is used.
         *
         * @param  array  $args
         * @param  string $ko_testdir
         * @return boolean
         */
        protected function is_using_xml_config ( array $args, $ko_testdir ) {
            
            $has_config = (
                   in_array( '-c', $args )
                or in_array( '--configuration', $args )
                or (
                    ! in_array( '--no-configuration', $args )
                    and (
                           file_exists( "$ko_testdir/phpunit.xml" )
                        or file_exists( "$ko_testdir/phpunit.xml.dist" )
                    )
                )
            );
            
            return $has_config;
            
        }
        
        /**
         * Alias of chdir(). Used to improve testability (can be mocked).
         * 
         * @param  string $dirpath
         * @return void
         */
        protected function set_working_dir( $dirpath ) {
            
            chdir( $dirpath );
            
        }
        
        public function handle_fatal_error () {
            
            if ( $this->premature_exit ) print <<<FATALERROR
            
@test_started@: +++ FATAL ERROR DURING TEST EXECUTION +++
@fault@:
The error location cannot be captured at this stage. Check the test summary for
the stack trace.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Category: error
@test_result@: E
FATALERROR;

        }
        
        protected function showHelp() {
            
            PHPUnit_TextUI_TestRunner::printVersionString();
            
            print <<<EOT
PHPUnit test harness for Komodo, version 1.2.0, by Michael Heim

Usage: [switches] UnitTest [UnitTest.php]
       [switches] <directory>

  Switches recognised by the test harness:
    
  --in-groups          Display test results grouped by status, problems first. Default.
  --in-sequence        Display test results in order of execution.

  --as-text            Convert test names to descriptive text. Default.
  --as-name            Display test names as in the source.

  --show-class         Show the name of the testcase class along with the method name. Default.
  --hide-class         Show the name of the test method only.

  --show-passed        Display the names of all tests. Default.
  --hide-passed        Display the names of failing tests only (including skipped and incomplete tests).

  --show-summary       Show the test summary generated by PHPUnit.
  --no-summary         Don't show the PHPUnit test summary.

  --help               Prints this usage information.
  
  Switches recognised by PHPUnit can also be used, although some might not work as expected.

EOT;
            parent::showHelp();
            
        }
        
    }
    
?>