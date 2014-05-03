
<?php
 
    echo <<<EOT
    <script src="ajaxPage.js"></script>
EOT;
    
    
    //////////////////
    //$result :容器的id
    //$url:请求的url
    //$total:总条数
    //$num：页容量
    //$pagenum:总页数
    //$page:当前页
    //$prepg:上一页
    //$nextpg:下一页
    //offset:limit后面的那个
    ////////////////
    function ajaxPage($result,$url,$total,$num=20)
    {
        global $page,$pagenum,$prepg,$nextpg,$offset;
        $GLOBALS["num"]=$num;
        $page=isset($_GET['page'])?intval($_GET['page']):1; //这句就是获取page=18中的page的值，假如不存在page，那么页数就是1。
        //$url='test1.php';//获取本页URL
        $pagenum=ceil($total/$num);    //获得总页数,也是最后一页
        $page=min($pagenum,$page);//获得首页
        $prepg=$page-1;//上一页
        $nextpg=($page==$pagenum ? 0 : $page+1);//下一页
        $offset=($page-1)*$num;
        
        //开始分页导航条代码：
        if($total==$offset+1){
            $pagenav="显示第 <B>".$total."</B> 条记录，共 $total 条记录 ";
        }else{
            $pagenav="显示第 <B>".($total?($offset+1):0)."</B>-<B>".min($offset+$num,$total)."</B> 条记录，共 $total 条记录 ";
        }
        
        //如果只有一页则跳出函数：
        if($pagenum<1)
        {
            return false;
        }
        //获取url
        if(strpos($url,"?")){
            $firstPg =$url."&page=1";
            $prePg = $url."&page=".$prepg;
            $nextPg = $url."&page=".$nextpg;
            $lastPg=$url."&page=".$pagenum;
        }else{
            $firstPg =$url."?page=1";
            $prePg = $url."?page=".$prepg;
            $nextPg = $url."?page=".$nextpg;
            $lastPg=$url."?page=".$pagenum;
        }
        $pagenav.=" <a href=javascript:dopage('$result','$firstPg');>首页</a> ";
        if($prepg) $pagenav.=" <a href=javascript:dopage('$result','$prePg');>上一页</a> "; else $pagenav.=" 上一页 ";
        if($nextpg) $pagenav.=" <a href=javascript:dopage('$result','$nextPg');>下一页</a> "; else $pagenav.=" 下一页";
        $pagenav.=" <a href=javascript:dopage('$result','$lastPg');>末页</a> ";
        $pagenav.="</select> 页，共 $pagenum 页";
        return $pagenav;
        
        //假如传入的页数参数大于总页数，则显示错误信息
        if($page>$pagenum){
            Echo "Error : Can Not Found The page ".$page;
            Exit;
        }
        //echo $num;
        
        
        
    }
    

    ?>