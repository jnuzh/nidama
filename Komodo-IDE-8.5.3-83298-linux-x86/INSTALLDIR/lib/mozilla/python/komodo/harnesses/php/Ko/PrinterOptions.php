<?php
    
    /**
     * @author  Michael Heim
     * @link    http://www.zeilenwechsel.de/
     * @version 1.0.0
     * @license http://www.zeilenwechsel.de/it/code/browse/komodo-phpunit-harness/prod/license.txt
     */
    
    require_once( dirname( dirname( __file__ ) ) . '/Utils/Loader.php' );
    PHPUnitXt_Utils_Loader::load( 'PHPUnitXt_Base_PrinterOptions' );
    
    
    class PHPUnitXt_Ko_PrinterOptions extends PHPUnitXt_Base_PrinterOptions {
        
        public function __construct () {
            
            parent::__construct();
            
            // Adding a new option.
            $this->define_option( 'force-new-harness' );
            
            // Setting the defaults.
            $this->set( 'in-groups' );
            $this->set( 'as-text' );
            $this->set( 'show-class' );            
            $this->set( 'show-passed' );          // change to 'hide-passed' once reporting in Komodo is fixed.
            $this->set( 'show-summary' );         // change to 'hide-summary' once reporting in Komodo is fixed.
            
            $this->set( 'force-new-harness', false );
            
        }
        
    }
    
?>