$(document).ready(function(){

    $("div#delete").hide();
    $("span#display_table").hide();

    $("span#display_chart").click(function(){
        $("span#display_chart").hide("fast");
        $("span#display_table").show("fast");
        $("div#add_course").hide("fast");
        $("div#delete").show("fast");
    });

    $("span#display_table").click(function(){
        $("span#display_table").hide("fast");
        $("span#display_chart").show("fast");
        $("div#delete").hide("fast");
        $("div#add_course").show("fast");
    });

});