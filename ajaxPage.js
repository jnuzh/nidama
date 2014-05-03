
var http_request=false;
var ajax_type;
var redirect_url;
/*
 
 0表示为了获取文本信息
 1表示执行一段逻辑代码
 2表示执行逻辑代码后进行重定向。
 
 
 */
function send_request(url)
{
    http_request=false;
    //开始初始化XMLHttp对象
    if(window.XMLHttpRequest){//MOILLA浏览器
        
        http_request=new XMLHttpRequest();
        if(http_request.overrideMimeType){
            http_request.overrideMimeType("text/xml");
            
        }
        
    }
    else if(window.ActiveXObject){//IE 浏览器
        try{
            http_request=new ActiveXObject("Msxml2.XMLHttp");
        }catch(e){
            try{
                http_request=new ActiveXObject("Microsoft.XMLHttp");
            }catch(e){}
            
        }
        
    }if(!http_request){
        window.alert("创建XMLHttp对象失败");
        return false;
        
    }
    http_request.onreadystatechange=processrequest;
    //确定发送请求方式，URL，及是否同步执行下段代码
    http_request.open("GET",url,true);
    http_request.send(null);
    
}
//处理返回信息函数
function processrequest(){
    //alert(reobj);
    if(http_request.readyState==4){
        if(http_request.status==200){
            switch(ajax_type){
                case 0:{
                    document.getElementById(reobj).innerHTML=http_request.responseText;
                }break;
                case 1:{
                    location.href=redirect_url;
                }break;
                default:{
                    
                }break;
            }
            
            
            //alert(http_request.responseText);

        }else{
            alert("您所请求的页面不正常");
        }
    }
}
function dopage(obj,url){
    
   // alert(222);
  //  document.getElementById(obj).innerHTML="正在读取数据.....";
    ajax_type=0;
    reobj=obj;
    send_request(url);
    
}
function dopage_ex(obj,url1,url2){
    ajax_type=1;
    reobj=obj;
    send_request(url1);
    redirect_url=url2;
    
}