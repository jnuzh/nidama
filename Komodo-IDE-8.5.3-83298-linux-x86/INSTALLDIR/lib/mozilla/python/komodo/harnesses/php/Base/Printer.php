<?php
    
    /**
     * @author  Michael Heim
     * @link    http://www.zeilenwechsel.de/
     * @version 1.1.0
     * @license http://www.zeilenwechsel.de/it/code/browse/komodo-phpunit-harness/prod/license.txt
     */
    
    require_once( 'PHPUnit/Runner/Version.php' );
    
    require_once( dirname( dirname( __file__ ) ) . '/Utils/Loader.php' );
    PHPUnitXt_Utils_Loader::load( 'PHPUnitXt_Base_PrinterOptions' );
    
    
    /**
     * Prints the test results in a configurable format.
     */
    class PHPUnitXt_Base_Printer extends PHPUnit_TextUI_ResultPrinter implements PHPUnit_Framework_TestListener {
        
        /* @var PHPUnitXt_Base_PrinterOptions */
        protected $options;
        
        protected $all_tests = array();
        protected $all_reports = array();
        
        /* @var array  paths to be removed from a stack trace; for use with PHPUnit 3.6 */
        protected $blacklist = array();
        
        public function __construct() {
            
            parent::__construct();
            
            $this->options = new PHPUnitXt_Base_PrinterOptions();
            
        }
        
        /**
         * Accepts the paths which must be removed from a stack trace. For use with
         * PHPUnit 3.6.
         * 
         * @param  array $blacklist
         * @return PHPUnitXt_Base_Printer
         */
        public function set_blacklist ( array $blacklist ) {
            
            $this->blacklist = $blacklist;
            return $this;
            
        }
        
        /**
         * @param PHPUnitXt_Base_PrinterOptions $options
         * @return void
         */
        public function set_all_options ( PHPUnitXt_Base_PrinterOptions $options ) {
            
            $this->options = $options;
            
        }
        
        /**
         * @param string  $name
         * @param mixed   $value   
         * @return void
         */
        public function set_option ( $name, $value = true ) {
            
            $this->options->set( $name, $value );
            
        }
        
        /**
         * Returns an array of all switches accepted by this printer.
         *
         * Names only, without leading '--'.
         *
         * @return array
         */
        public function get_switch_names () {
            
            return $this->options->get_option_names();
            
        }
        
        /**
         * @param  array   $defects
         * @param  integer $count
         * @param  string  $type
         */
        protected function printDefects( array $defects, $count, $type ) {
            
            if ( $count == 0 ) return;
            
            $i = 1;
            
            // Buffer and store the output for reordering if the defects are not grouped by type.
            $buffered = ( ! $this->options->get( 'in-groups' ) );
            
            foreach ( $defects as $defect ) {
                
                $buffer = $this->print_extended_defect_info( $defect, $i++, $type, $buffered );
                if ( $buffered ) {
                    
                    $testname = PHPUnit_Util_Test::describe( $defect->failedTest() );
                    $this->all_reports[$testname] = $buffer;
                    
                }
                
            }
            
        }
        
        /**
         * @param  PHPUnit_Framework_TestFailure $defect
         * @param  integer                       $count
         * @param  string                        $type
         * @param  bool                          $buffered
         * @return void|string
         */
        protected function print_extended_defect_info ( PHPUnit_Framework_TestFailure $defect, $count, $type, $buffered ) {
            
            if ( $buffered ) ob_start();
            
            $this->printDefect( $defect, $count );
            $this->write( "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\nCategory: $type\n" );
            
            if ( $buffered ) return ob_get_clean();
            
        }
        
        /**
         * @param  string $buffer
         */
        public function write( $buffer ) {
            
            // A bit of a hack to intercept the version string announcing PHPUnit before it's printed;
            // done for --hide-summary. Unclean, but all else is worse.
            $hide_summary = $this->options->get( 'hide-summary' );
            if ( $hide_summary and $buffer === PHPUnit_Runner_Version::getVersionString() . "\n\n" ) return;
            
            print $buffer;
            
            if ( $this->autoFlush ) {
                $this->incrementalFlush();
            }
            
        }
        
        /**
         * @param  PHPUnit_Framework_Test $test
         */
        public function startTest( PHPUnit_Framework_Test $test ) {
            
            $this->all_tests[] = PHPUnit_Util_Test::describe( $test );
            parent::startTest( $test );
            
        }
    
        /**
         * @param  PHPUnit_Framework_TestResult $result
         */
        public function printResult( PHPUnit_Framework_TestResult $result ) {
            
            $display_failed_tests_only = $this->options->get( 'hide-passed' );
            $display_order_by_status   = $this->options->get( 'in-groups' );
            $show_summary              = $this->options->get( 'show-summary' );
            
            // Printing the test summary.
            if ( $show_summary ) {
                
                print 'Using PHP ' . phpversion() . '.';
                if ( version_compare( PHPUnit_Runner_Version::id(), '3.5.0', '<' ) ) {
                    $this->printHeader(0);  // PHPUnit 3.4
                } else {
                    $this->printHeader();   // PHPUnit 3.5
                }
                
                $this->write( "---\n" );
                $this->printFooter( $result );
                
            }
            
            // Printing the tests.
            // NB: If tests are to be ordered by execution and, therefore, failures can't be printed as groups,
            // failure output will be intercepted and written to an array first ($this->all_reports).
            if ( $result->errorCount()   > 0 ) $this->printErrors( $result );
            if ( $result->failureCount() > 0 ) $this->printFailures( $result );
            if ( $result->skippedCount() > 0 ) $this->printSkipped( $result );
            if ( $result->notImplementedCount() > 0 ) $this->printIncompletes( $result );
                
            if ( $display_order_by_status ) {
                
                if ( count( $result->passed() ) > 0 and ! $display_failed_tests_only ) $this->print_passed_tests( $result );
                
            } else {
                
                $testnames = $this->all_tests;
                
                foreach ( $testnames as $testname ) {
                    
                    if ( array_key_exists( $testname, $this->all_reports ) ) {
                        
                        print $this->all_reports[$testname];
                        
                    } elseif ( ! $display_failed_tests_only ) {
                        
                        $this->print_passed_test( $testname );
                        
                    }
                    
                }
                
            }
            
        }
        
        /**
         * @param  string $progress
         */
        protected function writeProgress( $progress ) {
            
            $this->numTestsRun++;
            
        }
        
        /**
         * @param  PHPUnit_Framework_TestCase   $test
         * @return string                               the formatted test name
         */
        protected function get_formatted_test_name( PHPUnit_Framework_TestCase $test ) {
            
            $test_name = PHPUnit_Util_Test::describe( $test );
            return $this->format_test_name( $test_name );
            
        }
        
        /**
         * @param  string $test_name
         * @return string               the formatted test name
         */
        protected function format_test_name( $test_name ) {
            
            $no_formatting     = $this->options->get( 'as-name' );
            $remove_classnames = $this->options->get( 'hide-class' );
            
            if ( $no_formatting ) {
                
                $formatted_name = (
                    $remove_classnames ?
                    preg_replace( '%.+::%', '', $test_name ) :
                    $test_name
                );
                
            } else {
                
                if ( preg_match( '%^((?:.+::)?)(?:test)?(.+?)(?:test)?$%i', $test_name, $parts ) ) {
                    
                    $class = str_replace( '::', ' - ', $parts[1] );
                    $description = $parts[2];
                    
                } else {
                    
                    $class = '';
                    $description = $test_name;
                    
                }
                
                $description = preg_replace( "/([a-z_\d])([A-Z])/", "$1 $2", $description );
                
                if ( strpos( $description, '_' ) !== false ) {
                    $description[strpos( $description, '_' )] = ':';
                    $description = str_replace( '_', ',', $description );
                }
                
                $description = preg_replace_callback(
                    '/ ([A-Z])([a-z])/',
                    create_function(
                        '$matches',
                        'return " " . strtolower( $matches[1] ) . $matches[2];'
                    ),
                    $description
                );
                
                $formatted_name = ( $remove_classnames ? $description : $class . $description );
                
            }
            
            return $formatted_name;
            
        }
        
        /**
         * @param  PHPUnit_Framework_TestResult  $result
         */
        protected function print_passed_tests ( PHPUnit_Framework_TestResult $result ) {
            
            $passed = $result->passed();
            
            foreach( $passed as $name => $unused ) {
                
                $this->print_passed_test( $name );
                
            }
            
        }
        
        /**
         * @param string  $name
         */
        protected function print_passed_test ( $name ) {
            
            $displayed = $this->format_test_name( $name );
            print "\n$displayed\n";
            
        }
        
        /**
         * @param  PHPUnit_Framework_TestFailure $defect
         */
        protected function printDefectTrace( PHPUnit_Framework_TestFailure $defect ) {
            
            if ( version_compare( PHPUnit_Runner_Version::id(), '3.6.0', '<' ) ) {
                
                parent::printDefectTrace( $defect );
                
            } else {
                
                // In PHPUnit 3.6, we need to filter the test harness files from the
                // stack trace ourselves. There is no way to access and customize the
                // built-in filter, as there used to be in PHP 3.5.
                //
                // (Actually, the built-in filter can be manipulated - see StackOverflow
                // http://goo.gl/HP2el. But it doesn't work with PHP 5.2.)
                
                ob_start();
                parent::printDefectTrace( $defect );
                $trace = ob_get_clean();
                
                $lines = explode( "\n", $trace );
                $filtered_stacktrace = array();
                
                foreach( $lines as $line ) {
                    
                    $include = true;
                    foreach( $this->blacklist as $blacklisted ) {
                        
                        $include = ( stripos( $line, $blacklisted ) !== 0 );
                        if ( ! $include ) break;
                        
                    }
                    
                    if ( $include ) $filtered_stacktrace[] = $line;
                }
                
                $this->write( implode( "\n", $filtered_stacktrace ) );
                
            }
            
        }
        
    }
    
?>
