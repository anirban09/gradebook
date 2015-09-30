$(document).ready(function(){
    
    $("div#main_chart").hide();
    $("span#display_table").hide();

    $("span#display_chart").click(function(){
        $("span#display_chart").hide("fast");
        $("div#main_table").hide("fast");
        $("span#display_table").show("fast");
        $("div#main_chart").show("fast");
        setTimeout(function(){drawChart()},200);
    });

    $("span#display_table").click(function(){
        $("span#display_table").hide("fast");
        $("div#main_chart").hide("fast");
        $("span#display_chart").show("fast");
        $("div#main_table").show("fast");
    });

});