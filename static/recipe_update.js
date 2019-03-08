"use strict";

function getRecipe() {
    $('#new-random-recipe').on('submit', evt => {
        evt.preventDefault();

    const formData = {
        dietary: $('#dietary').val(),
        health: $('#health').val()
        };

    $.get('/display_random_recipe', formData, (results) => {
    $('url').attr('href', results.url);
    $('img').attr('src', results.image);
    $('recipe-name').html(results.label);
    });
});
}

getRecipe();