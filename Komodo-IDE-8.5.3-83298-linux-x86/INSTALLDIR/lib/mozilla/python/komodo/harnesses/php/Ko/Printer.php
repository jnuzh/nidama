<?php
    
    /**
     * @author  Michael Heim
     * @link    http://www.zeilenwechsel.de/
     * @version 1.0.0
     * @license http://www.zeilenwechsel.de/it/code/browse/komodo-phpunit-harness/prod/license.txt
     */
    
    require_once( dirname( dirname( __file__ ) ) . '/Utils/Loader.php' );
    PHPUnitXt_Utils_Loader::load( 'PHPUnitXt_Base_Printer' );
    
    
    /**
     * Prints the test results in a format suitable for Komodo.
     */
    class PHPUnitXt_Ko_Printer extends PHPUnitXt_Base_Printer implements PHPUnit_Framework_TestListener {
        
        const DISPLAY_FORMATTED_TESTNAMES = 0;
        const DISPLAY_TESTNAMES_WITH_CLASS = 1;
        const DISPLAY_FAILED_TESTS_ONLY = 2;
        const DISPLAY_ORDER_BY_STATUS = 3;
        
        public function __construct() {
            
            parent::__construct();
            
        }
        
        /**
         * @param  PHPUnit_Framework_TestFailure $defect
         * @param  integer                       $count
         * @param  string                        $type
         * @param  bool                          $buffered
         * @return void|string
         */
        protected function print_extended_defect_info ( PHPUnit_Framework_TestFailure $defect, $count, $type, $buffered ) {
            
            switch ( $type ) {
                case 'error':
                    $defect_code = 'E';
                    break;
                case 'failure':
                    $defect_code = 'F';
                    break;
                case 'incomplete test':
                    $defect_code = 'I';
                    break;
                case 'skipped test':
                    $defect_code = 'S';
                    break;
            }
            
            $test = $defect->failedTest();
            
            if ( $buffered ) ob_start();
            
            printf("@test_started@: %s\n", $this->get_formatted_test_name( $test ) );
            print "@fault@:\n";
            parent::print_extended_defect_info( $defect, $count, $type, false );
            printf("@test_result@: %s\n", $defect_code);
            
            if ( $buffered ) return ob_get_clean();
            
        }
        
        /**
         * @param  PHPUnit_Framework_TestResult $result
         */
        public function printResult( PHPUnit_Framework_TestResult $result ) {
            
            parent::printResult( $result );
            
            // Printing status info for evaluation by Komodo.
            $status = sprintf(
                " N:%d P:%d F:%d E:%d",
                count( $result ),
                count( $result->passed() ),
                $result->notImplementedCount(),
                $result->errorCount()
            );
            
            if ( $result->skippedCount() > 0 ) {
                $status .= sprintf(" S:%d", $result->skippedCount() );
            }
            
            if ( $result->notImplementedCount() > 0 ) {
                $status .= sprintf(" I:%d", $result->notImplementedCount() );
            }
            
            // NB: PHP_Timer might not be installed if PHPUnit < 3.5 is used
            $time_total = (
                class_exists( 'PHP_Timer' ) ?
                PHP_Timer::timeSinceStartOfRequest() :
                sprintf( "%.2F seconds", $result->time() )
            );
            printf( "@suite_finished@:%s; %s\n", $status, $time_total );
            
        }
        
        /**
         * @param string  $name
         */
        protected function print_passed_test ( $name ) {
            
            $displayed = $this->format_test_name( $name );
            printf("@test_started@: %s\n", $displayed );
            printf("@test_result@: %s\n", 'P' );
            
        }
        
    }
    
?>
