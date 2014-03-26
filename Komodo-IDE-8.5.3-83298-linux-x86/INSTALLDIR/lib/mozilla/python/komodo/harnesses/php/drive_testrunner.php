<?php
    
    /**
     * @author  Michael Heim
     * @link    http://www.zeilenwechsel.de/
     * @version 1.0.0
     * @license http://www.zeilenwechsel.de/it/code/browse/komodo-phpunit-harness/prod/license.txt
     */
    
    require_once( dirname( __file__ ) . '/Utils/Loader.php' );
    PHPUnitXt_Utils_Loader::load( 'PHPUnitXt_Ko_PrinterOptions' );
    PHPUnitXt_Utils_Loader::load( 'PHPUnitXt_Ko_HarnessSelector' );
    
    $selector = new PHPUnitXt_Ko_HarnessSelector( new PHPUnitXt_Ko_PrinterOptions() );
    $selector->run_harness( $_SERVER['argv'], $_SERVER['argc'] );
    
?>
