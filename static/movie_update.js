"use strict";

$(document).ready(function() {
    $('.movie-title-search').click(function() {
        $('#movie-title').show()
        $('#movie-filter').hide()

    });
    $('.movie-filter-search').click(function() {
        $('#movie-filter').show()
        $('#movie-title').hide()
    });

    $('#choose-movie').click(function() {
        // evt.preventDefault();
        $('.youtube').show()

        let formData = {'q': $('#movie-name').html()};
        console.log(formData)
        
        $.get('/get_youtube_video', formData, (results) => {
        $('#youtube-link').attr('href', "https://www.youtube.com/watch?v="+results);
        });
        });

    });