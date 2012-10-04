 $(function() {
    $('#search3423').bind('click', function() {
      $.getJSON($SCRIPT_ROOT + '/search_authors_books', {
        text: $('input[name="text"]').val()
      }, function(data) {
        if(data.result){
            $("#authors").append('<li>'+data.result+'</li>');
          }
      });
      return false;
    });
  });
$(function(){
  $("select").multiselect({
    selectedList: 4
  });
  
});