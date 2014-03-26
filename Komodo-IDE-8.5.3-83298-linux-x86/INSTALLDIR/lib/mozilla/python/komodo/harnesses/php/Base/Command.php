<?php
    
    /**
     * @author  Michael Heim
     * @link    http://www.zeilenwechsel.de/
     * @version 1.1.0
     * @license http://www.zeilenwechsel.de/it/code/browse/komodo-phpunit-harness/prod/license.txt
     */
    
    require_once( dirname( dirname( __file__ ) ) . '/Utils/Loader.php' );
    PHPUnitXt_Utils_Loader::load( 'PHPUnitXt_Base_Printer' );
    
    
    /**
     * A PHPUnit test runner for the command line. Supports additional output options.
     */
    class PHPUnitXt_Base_Command extends PHPUnit_TextUI_Command {
        
        protected $premature_exit = true;
        
        /**
         * @param boolean $exit
         */
        public static function main ( $exit = true ) {
            
            self::exec( $_SERVER['argv'], null, $exit );
            
        }
        
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
            
            $exit = ( $exit and ! self::suppress_termination() );
            
            $command = new PHPUnitXt_Base_Command();
            $command->set_printer( new PHPUnitXt_Base_Printer(), $printer_defaults, $blacklist )
                    ->register_fatal_error_handler()
                    ->run( $args, false );
            
            $command->has_run_all_tests();
            
            if ( $exit ) exit();
            
        }
        
        /**
         * Defines a callback method for each printer-specific option.
         *
         * They cover options not normally recognized by PHPUnit. The callback methods are invoked
         * as option handlers by PHPUnit.
         *
         * Callback names are made to begin with 'set_printer_option_', in order to avoid conflicts.
         * 
         * @param array $option_names   an array of switch names accepted by the printer
         * @return void
         */
        protected function define_option_handlers( array $option_names ) {
            
            foreach( $option_names as $name ) {
                
                $this->longOptions[ $name ] = 'set_printer_option_' . str_replace( '-', '_', $name );
                
            }
            
        }
        
        /**
         * Intercepts method calls for printer-specific option handlers.
         *
         * These method calls all originate from PHPUnit. They are made when a printer-specific
         * switch is encountered.
         * 
         * @param string $name
         * @param mixed $value
         * @return void
         */
        public function __call ( $name, $value = true ) {
            
            if ( substr( $name, 0, 19 ) == 'set_printer_option_' ) {
                
                $arg = str_replace( '_', '-', substr( $name, 19 ) );
                $this->set_printer_option( $arg, $value );
                
            } else {
                
                throw new Exception( "Invalid method call: $name" );
                
            }
            
        }
        
        /**
         * @param string $name
         * @param mixed  $value
         * @return void
         */
        protected function set_printer_option ( $name, $value = true ) {
            
            $this->arguments['printer']->set_option( $name, $value );
            
        }
        
        /**
         * Sets the printer and defines the option handlers, according to the options/switches accepted by this printer.
         * 
         * @param  PHPUnitXt_Base_Printer           $result_printer
         * @param  PHPUnitXt_Base_PrinterOptions    $printer_defaults
         * @param  array                            $blacklist              for use with PHPUnit 3.6
         * @return PHPUnitXt_Base_Command
         */
        public function set_printer ( PHPUnitXt_Base_Printer $result_printer, PHPUnitXt_Base_PrinterOptions $printer_defaults = null, array $blacklist = array() ) {
            
            $result_printer->set_blacklist( $blacklist );
            if( ! is_null( $printer_defaults ) ) $result_printer->set_all_options( $printer_defaults );
            $this->define_option_handlers( $result_printer->get_switch_names() );
            
            $this->arguments['printer'] = $result_printer;
            
            return $this;
            
        }
        
        /**
         * @return PHPUnitXt_Base_Command
         */
        public function register_fatal_error_handler () {
            
            register_shutdown_function ( array( $this, 'handle_fatal_error' ) );
            return $this;
            
        }
        
        /**
         * Cancels the execution of the fatal error handler on clean shutdown.
         * Call after all tests have run.
         * 
         * @return PHPUnitXt_Base_Command
         */
        public function has_run_all_tests () {
            
            $this->premature_exit = false;
            return $this;
            
        }
        
        public function handle_fatal_error () {
            
            if ( $this->premature_exit ) print "\n\n##########   Fatal error, execution aborted prematurely   ##########\n\n";
            
        }
        
        /**
         * Checks if a PHPUNIT_COMMAND_NOEXIT environment variable is set.
         *
         * This is used to allow overriding the $exit parameter in main() or exec(). Useful for debugging or
         * integration testing, where the $exit parameter is usually hard-coded in the initial call.
         * 
         * @return bool
         */
        protected static function suppress_termination () {
            
            return getenv( 'PHPUNIT_COMMAND_NOEXIT' );
            
        }
        
    }
    
?>