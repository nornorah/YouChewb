"use strict";

$(document).ready(function() {
    $('#movie-title-search').click(function() {
        $('#movie-title').show()
        $('#movie-filter').hide()

    });
    $('#movie-filter-search').click(function() {
        $('#movie-filter').show()
        $('#movie-title').hide()
    });

    $('#choose-movie').click(function() {
        $('#youtube').show()

        let formData = {'q': $('#movie-name').val()};
        console.log(formData)
        
        $.get('/get_youtube_video', formData, (results) => {
        $('#youtube-link').attr('src', "https://www.youtube.com/embed/"+results);
        });
        });

    });

// <div class="container-fluid page-top">

// <div class="card col-xl-2 col-lg-3 col-md-4 col-s-6 col-xs-6">

//     <div class="card-image waves-effect waves-block waves-light">
//       <img class="activator" src="{{ recipe_image }}">
//     </div>
//     <div class="card-content">
//       <span class="card-title activator grey-text text-darken-4" style="font-size:16px; font-family: 'Staatliches', cursive;">{{ recipe_name }}<i class="material-icons right">more_vert</i></span>
//       <p><a href="{{ recipe['url'] }}" style="color: #757575">cooking instructions</a></p>
//     </div>
//     <div class="card-reveal">
//       <span class="card-title grey-text text-darken-4">{{ recipe['label'] }}<i class="material-icons right">close</i></span>
//       <p>You'll need: <br>
//       {{ '; '.join(recipe['ingredientLines']) }}</p>
//     </div>
//   </div>