$(document).ready(function(){

    $("div#edit_profile").hide();
    $("span#display_table").hide();

    $("span#display_chart").click(function(){
        $("span#display_chart").hide("fast");
        $("span#display_table").show("fast");
        $("div#profile").hide("fast");
        $("div#edit_profile").show("fast");
    });

    $("span#display_table").click(function(){
        $("span#display_table").hide("fast");
        $("span#display_chart").show("fast");
        $("div#edit_profile").hide("fast");
        $("div#profile").show("fast");
    });

});