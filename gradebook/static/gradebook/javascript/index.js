$(document).ready(function(){

    $("span#registration").click(function(){
        $("div#logo").animate({"top": "10%"}, 200);
        $("div#login").hide("fast");
        $("div#register").show("fast");
    });

    $("span#login").click(function(){
        $("div#logo").animate({"top": "20%"}, 200);
        $("div#register").hide("fast");
        $("div#login").show("fast");
    });

    $("div#error").click(function(){
        $("div#error").hide("fast");
    });

});