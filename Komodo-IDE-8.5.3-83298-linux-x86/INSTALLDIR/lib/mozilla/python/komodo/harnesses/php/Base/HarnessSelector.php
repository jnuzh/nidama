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
    
    
    class PHPUnitXt_Base_HarnessSelector {
        
        protected $ver_phpunit, $root;
        
        /* @var PHPUnitXt_Base_PrinterOptions */
        protected $defaults;
        
        /* @var array  for PHPUnit 3.6 */
        protected $blacklist = array();
        
        public function __construct ( PHPUnitXt_Base_PrinterOptions $defaults ) {
            
            $this->defaults = $defaults;
            $this->ver_phpunit = $this->get_phpunit_version();
            $this->root = PHPUnitXt_Utils_Loader::root();
            
        }
        
        public function run_harness( $argv, $argc ) {
            
            $this->prepare_harness();
            
            PHPUnitXt_Utils_Loader::load( 'PHPUnitXt_Base_Command' );
            PHPUnitXt_Base_Command::exec( $argv, $this->defaults, $this->blacklist );
            
        }
        
        public function get_phpunit_version( $as_string = false ) {
            
            $ver = PHPUnit_Runner_Version::id();
            
            if ( ! $as_string ) {
                $ver_array = explode( '.', $ver );
                $ver_array[0] .= '.';
                $ver = (float) implode( '', $ver_array );
            }
            
            return $ver;
            
        }
        
        protected function prepare_harness() {
            
            if ( $this->ver_phpunit < 3.5 ) {
                
                require_once( 'PHPUnit/Framework.php' );
                require_once( 'PHPUnit/TextUI/ResultPrinter.php' );
                require_once( 'PHPUnit/TextUI/Command.php' );
                
                PHPUnit_Util_Filter::addDirectoryToFilter( $this->root, '.php', 'PHPUNIT', '' );
                
            } elseif ( $this->ver_phpunit < 3.6 ) {
                
                require_once( 'PHPUnit/Autoload.php' );
                require_once( 'PHP/CodeCoverage.php' );
                
                PHP_CodeCoverage::getInstance()->filter()->addDirectoryToBlacklist( $this->root, '.php', '', 'PHPUNIT' );
            
            } else {
                
                // PHPUnit 3.6+
                
                require_once( 'PHPUnit/Autoload.php' );
                require_once( 'PHP/CodeCoverage.php' );
                
                $this->add_directory_to_blacklist( $this->root, '.php' );
                
            }
            
        }
        
        /**
         * Adds a directory to the blacklist (recursively). For use with PHPUnit 3.6.
         *
         * NB: There is a way to modify the internal blacklist directly. It would
         * involve creating a PHPUnit_Util_GlobalState reflector and calling
         * setAccessible() on it. This is suggested on StackOverflow, http://goo.gl/HP2el.
         * But it requires PHP 5.3.
         *
         * @param  string $directory
         * @param  string $suffix
         * @return PHPUnitXt_Base_HarnessSelector
         */
        protected function add_directory_to_blacklist ( $directory, $suffix = '.php' ) {
            
            $dirpath = realpath( $directory );
            $filepaths = array();
            
            if ( is_dir( $dirpath ) ) {
                
                $dir_iterator = new RecursiveDirectoryIterator( $dirpath );
                
                /* @var $file DirectoryIterator */
                foreach ( new RecursiveIteratorIterator( $dir_iterator ) as $file ) {
                    
                    $path = $file->getPathname();
                    if ( $suffix === '' or substr( $path, - strlen( $suffix ) ) == $suffix ) $this->add_file_to_blacklist( $path );
                    
                }
                
            }
            
            return $this;
            
        }
        
        /**
         * Adds a file to the blacklist. For use with PHPUnit 3.6.
         *
         * NB: realpath() is invoked here.
         *
         * @param  string  $filepath
         * @param  boolean $avoid_duplicates
         * @return PHPUnitXt_Base_HarnessSelector
         */
        protected function add_file_to_blacklist ( $filepath, $avoid_duplicates = false ) {
            
            $path = realpath( $filepath );
            
            if ( $avoid_duplicates ) {
                if ( in_array( $path, $this->blacklist ) ) $path = false;
            }
            
            if ( $path !== false ) $this->blacklist[] = $path;
            return $this;
            
        }
        
    }
    
?>
