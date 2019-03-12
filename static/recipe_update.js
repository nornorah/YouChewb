"use strict";

$(document).ready(function() {
    function getGenre(){
    let genreArray = [];
    $(".genre:checked").each(function() {
        genreArray.push($(this).val());
    });
    return genreArray
    };

    let dietary = null;
    let peanut = null;
    let vegetarian = null;
    let health = [];


    $("#recipe-no").click( function() {
        $("#dietary").show();
    });

    $(".dietary").click(function() {
    $("#peanut").show();
        dietary = $(this).val();
    });

    $(".peanut").click(function() {
        $("#vege").show();
        peanut = $(this).val();
    });

    $(".vege").click(function() {
        vegetarian = $(this).val();
        $("#submit-button-recipe").show();
    });

    $('#new-random-recipe').click(function() {
        
        let formData = {};

        if (peanut) {
        health.push(peanut);
        };

        if (vegetarian) {
        health.push(vegetarian);
        };

        if (dietary && health){
            formData = {
            'dietary': dietary,
            'health': health
            };

        } else if (dietary){
            formData = {
            'dietary': dietary
            };

        } else if (health){
            formData = {
            'health': health
            };
        }

        $.get('/get_random_recipe', formData, (results) => {
        $('#recipe-url').attr('href', results.url);
        $('#recipe-img').attr('src', results.image);
        $('#recipe-name').html(results.label);
        $('#recipe-ingredients').html((results.ingredientLines).join('; '))
        $('#new-random-recipe').attr('value', "Give Me Another One")
        });    
        });

        $("#recipe-yes").click(function() {
        $("#movie").show();
        });

    let genre = null;
    let year = null;
    // let gte = null;
    // let lte = null;

    $("#movie-no").click(function() {
        $("#genre-checkbox").show();
    });

    $(".genre").click(function() {
        genre = getGenre();
        $("#year-radio").show().delay(5000);
    });

    $(".year").click(function() {
        $("#submit-button-movie").show();
    });

    $('#new-random-movie').click(function() {
        
        let formData = {};

        if (genre){
            formData['with_genres'] = genre
        };
        if (gte){
            formData['release_date.gte'] = $('#gte').val()
        }; 

        if (lte){
            formData['release_date.lte'] = $('#lte').val()
        };         

        console.log(formData)
        $.get('/get_random_movie', formData, (results) => {
            console.log(results)
            $('#movie-url').attr('href', "https://www.themoviedb.org/movie/"+results.id);
            $('#movie-img').attr('src', "https://image.tmdb.org/t/p/w500/"+results.poster_path);
            $('#movie-name').html(results.title);
            $('#movie-overview').html((results.overview))
            $('#new-random-movie').attr('value', "Give Me Another One")
            });
        });

    $("#movie-yes").click(function(evt) {
        evt.preventDefault();

        $("#youtube").show();

        let formData = {'q': $('#movie-name').html()};

        $.get('/get_youtube_video', formData, (results) => {
        $('#youtube-link').attr('href', "https://www.youtube.com/watch?v="+results);
        });
    });

})








