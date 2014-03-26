<?php
    
    /**
     * @author  Michael Heim
     * @link    http://www.zeilenwechsel.de/
     * @version 1.1.0
     * @license http://www.zeilenwechsel.de/it/code/browse/komodo-phpunit-harness/prod/license.txt
     */
    
    require_once( dirname( dirname( __file__ ) ) . '/Utils/Loader.php' );
    PHPUnitXt_Utils_Loader::load( 'PHPUnitXt_Base_HarnessSelector' );
    
    
    class PHPUnitXt_Ko_HarnessSelector extends PHPUnitXt_Base_HarnessSelector {
        
        public function run_harness( $argv, $argc ) {
            
            if ( $this->ver_phpunit < 3.5 and ! $this->force_new_harness() ) {
                
                chdir( $this->root . DIRECTORY_SEPARATOR . 'legacy' );
                require_once( $this->root . '/legacy/drive_testrunner.php' );
                
            } else {
                
                $this->prepare_harness();
                
                PHPUnitXt_Utils_Loader::load( 'PHPUnitXt_Ko_Command' );
                PHPUnitXt_Ko_Command::exec( $argv, $this->defaults, $this->blacklist );
                
            }
            
        }
        
        protected function force_new_harness () {
            
            $force_new = $this->defaults->get( 'force-new-harness' );
            
            $params = $_SERVER['argv'];
            
            foreach( $params as $param ) {
                if ( strpos( $param, '--force-new-harness' ) !== false ) $force_new = true;
            }
            
            return $force_new;
            
        }
        
    }
    
?>
