<?php
    
    /**
     * @author  Michael Heim
     * @link    http://www.zeilenwechsel.de/
     * @version 1.0.0
     * @license http://www.zeilenwechsel.de/it/code/browse/komodo-phpunit-harness/prod/license.txt
     */
    
    require_once( dirname( dirname( __file__ ) ) . '/Utils/Loader.php' );
    PHPUnitXt_Utils_Loader::load( 'PHPUnitXt_Base_PrinterOptions' );
    PHPUnitXt_Utils_Loader::load( 'PHPUnitXt_Base_HarnessSelector' );
    
    $selector = new PHPUnitXt_Base_HarnessSelector( new PHPUnitXt_Base_PrinterOptions() );
    $selector->run_harness( $_SERVER['argv'], $_SERVER['argc'] );
    
?>
