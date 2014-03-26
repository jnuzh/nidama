<?php
    
    /**
     * @author  Michael Heim
     * @link    http://www.zeilenwechsel.de/
     * @version 1.0.0
     * @license http://www.zeilenwechsel.de/it/code/browse/komodo-phpunit-harness/prod/license.txt
     */
    
    class PHPUnitXt_Utils_Loader {
        
        /**
         * Loads a class.
         * 
         * @param string $classname
         * @return void
         */
        public static function load ( $classname ) {
            
            require_once( self::to_path( $classname ) );
            
        }
        
        /**
         * Returns the root directory of the custom PHPUnit extensions. Trailing slash not included.
         * 
         * @return string
         */
        public static function root () {
            
            return dirname( dirname( __file__ ) );
            
        }
        
        /**
         * Resolves a classname to a file path.
         * 
         * @param  string $classname
         * @return string
         */
        protected static function to_path ( $classname ) {
            
            $root = self::root();
            
            $classpath = str_replace( 'PHPUnitXt_', '', $classname );
            $classpath = str_replace( '_', '/', $classpath );
            
            return realpath( "$root/$classpath.php" );
            
        }
        
    }
    
?>