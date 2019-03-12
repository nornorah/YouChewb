// "use strict";
// $(document).ready(function() {
//     $('#recipe-search').click(function() {
//     let calories = $('#calories').val()
//     console.log(calories)

//     let health = [];
//     $(".health:checked").each(function(){
//         health.push($(this).val());
//     });

//     let formData = {'q': $('#search').val(),
//                     'calories': calories,
//                     'dietary': $('#dietary').val(),
//                     'health': health}
//     console.log(formData)

//     $.get('/display_recipe_search_results', formData, (results) => {
//         results.forEach(element => {$('#recipe-name').html(element.label);
//         })
//         console.log(results)

//         });
//     });

// });