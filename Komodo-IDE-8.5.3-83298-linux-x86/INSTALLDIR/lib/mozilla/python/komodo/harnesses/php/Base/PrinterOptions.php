<?php
    
    /**
     * @author  Michael Heim
     * @link    http://www.zeilenwechsel.de/
     * @version 1.0.0
     * @license http://www.zeilenwechsel.de/it/code/browse/komodo-phpunit-harness/prod/license.txt
     */
    
    class PHPUnitXt_Base_PrinterOptions {
        
        /* @var array   the option names */
        protected $option_names;
        
        /* @var array   the names of their opposites (keys), and the options they relate to (values) */
        protected $opposites;
        
        /* @var array   the options and their values */
        protected $options;
        
        public function __construct () {
            
            // Defining the available options.
            $this->define_option( 'in-groups',    'in-sequence' );
            $this->define_option( 'as-text',      'as-name' );
            $this->define_option( 'show-class',   'hide-class' );
            $this->define_option( 'show-passed',  'hide-passed' );
            $this->define_option( 'show-summary', 'hide-summary' );
            
            // Setting the defaults.
            $this->set( 'in-groups' );
            $this->set( 'as-text' );
            $this->set( 'show-class' );            
            $this->set( 'hide-passed' );
            $this->set( 'show-summary' );
            
        }
        
        /**
         * Registers the name of an option and, optionally, the name of a complementary,
         * opposite option. The primary option will be set to true.
         * 
         * @param string $name
         * @param string $opposite
         * 
         * @return void
         */
        protected function define_option( $name, $opposite = null ) {
            
            $this->option_names[] = $name;
            $this->options[$name] = true;
            
            if ( ! empty( $opposite ) ) $this->opposites[$opposite] = $name;
            
        }
        
        /**
         * @param  string $name the option
         * @return bool
         */
        public function get ( $name ) {
            
            if ( array_key_exists( $name, $this->options ) ) {
                
                return $this->options[$name];
                
            } elseif ( array_key_exists( $name, $this->opposites ) ) {
                
                return ( ! $this->options[ $this->opposites[$name] ] );
                
            } else {
                
                throw new Exception( "\nUnknown option $name\n" );
                
            }
            
        }
        
        /**
         * @param string $name
         * @param bool   $value
         * @return void
         */
        public function set ( $name, $value = true ) {
            
            if ( array_key_exists( $name, $this->options ) ) {
                
                $this->options[$name] = $value;
                
            } elseif ( array_key_exists( $name, $this->opposites ) ) {
                
                $this->options[ $this->opposites[$name] ] = ( ! $value );
                
            } else {
                
                throw new Exception( "\nUnknown argument --$name\n" );
                
            }
            
        }
        
        /**
         * Returns an array of all defined options.
         *
         * @param  bool      $include_opposites    include the names of complementary, opposite options in the array
         * @return array
         */
        public function get_option_names ( $include_opposites = true ) {
            
            return (
                $include_opposites ?
                array_merge( $this->option_names, array_keys( $this->opposites ) ) :
                $this->option_names
            );
            
        }
        
        /**
         * Returns the name of the complementary, opposite option if it exists, or an empty string otherwise.
         * 
         * @param  string  $name
         * @return string
         */
        public function get_opposite_option_name ( $name ) {
            
            if ( array_key_exists( $name, $this->opposites ) ) {
                
                $opposite = $this->opposites[$name];
                
            } else {
                
                $opposite = (string) array_search( $name, $this->opposites );    // returns false if not found, forced to ''
                
            }
            
            return $opposite;
            
        }
        
    }
    
?>