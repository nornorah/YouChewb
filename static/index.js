    <div id="movie" class="col-xs-6 right" style="margin-right:15px; display:none;">

<h3 class="title" style="font-family: 'Cabin Sketch', cursive;">...and this to watch?</h3>
          <a href="{{ movie_url }}" id="movie-url" target="_blank">
            <img src="{{ movie_image }}" id="movie-img" style="width:350px; height:450px"></a>
          <br>
        <div id="movie-name">
          {{ movie['title'] }} 
        </div>  
        <br>
        Synopsis:
        <div id="movie-overview">
        {{ movie['overview'] }}
        <br>
      </div>
  <br>
      <div id="happy-movie">
      Want to Chewse This?
      <br>
          <button class="happy-movie-button" id="movie-yes" value="yes">Yes. Give Me the YouTube Link</button>
          <br>
          <button class="happy-movie-button" id="movie-no" value="no">No. Give Me Other Choices</button>
      </div> 

        <br>
    <div id="genre-checkbox" style="display:none">
    Filter by Genre?
    <br>
      <input type="checkbox" class="genre" value="action">Action</input>
      <input type="checkbox" class="genre" value="adventure">Adventure</input>
      <input type="checkbox" class="genre" value="animation">Animation</input>
      <input type="checkbox" class="genre" value="comedy">Comedy</input>
      <br>
      <input type="checkbox" class="genre" value="crime">Crime</input>
      <input type="checkbox" class="genre" value="documentary">Documentary</input>
      <input type="checkbox" class="genre" value="drama">Drama</input>
      <input type="checkbox" class="genre" value="family">Family</input>
      <br>
      <input type="checkbox" class="genre" value="fantasy">Fantasy</input>
      <input type="checkbox" class="genre" value="war">War</input>
      <input type="checkbox" class="genre" value="horror">Horror</input>
      <input type="checkbox" class="genre" value="mystery">Mystery</input>
      <br>
      <input type="checkbox" class="genre" value="romance">Romance</input>
      <input type="checkbox" class="genre" value="science fiction">Sci-Fi</input>
      <input type="checkbox" class="genre" value="thriller">Thriller</input>      
      <input type="checkbox" class="genre" value="history">History</input>  
      <br>
    </div>
    <br>
    <div id="year-radio" style="display:none">
        Filter by Year Released?
        <br>
        <input type="text" id="gte" placeholder="Released after" class="year">
        <input type="text" id="lte" placeholder="Released before" class="year">
        <input type="radio" class="year" value="" name="year">No Preference</input>
    </div>

    <div id="submit-button-movie" style="display:none">
      <input type="submit" value="Filter and Get a New Movie" id="new-random-movie">
    </div>
        

<div id="youtube" style="display:none">
  <a href="" id="youtube-link" target="_blank"><input type="submit" value="Watch This Movie On YouTube"></a>
  <form action="/save_activity">
    <input type="submit" value="All Done - Save This Activity" id="all-done">
  </form>
</div>
</div>
</div>






<br>
<br>
<div class="row">


<h4 style="font-family: 'Cabin Sketch', cursive;">{{ date }}</h4>
<div class="card card-cascade wider reverse col-xl-6 col-lg-6 col-md-6 col-sm-6 col-xs-6 m-1 p-1">

  <!-- Card image -->
  <div class="view view-cascade overlay">
    <img class="card-img-top" src="{{ recipe.recipe_image }}">
    <a href="{{ recipe.recipe_url }}" target="_blank">
      <div class="mask flex-center rgba-white-light"><p class="white-text" style="font-size:20px;">INSTRUCTIONS</p></div>
    </a>
  </div>
  <!-- Card content -->
  <div class="card-body card-body-cascade text-center">

    <!-- Title -->
    <h4 class="card-title" style="font-size:20px; font-family: 'Cabin Sketch', cursive;">{{ recipe.recipe_name }}</h4>
    </p>
</div>

  </div>
  <div class="card card-cascade wider reverse col-xl-6 col-lg-6 col-md-6 col-sm-6 col-xs-6 m-1 p-1">

  <!-- Card image -->
  <div class="view view-cascade overlay">
    <img class="card-img-top" src="{{ movie.movie_image }}">
    <a href="{{ movie.movie_url }}" target="_blank">
      <div class="mask flex-center rgba-white-light"><p class="white-text" style="font-size:20px;">INFORMATION</p></div>
    </a>
  </div>

  <!-- Card content -->
  <div class="card-body card-body-cascade text-center">

    <!-- Title -->
    <h4 class="card-title" style="font-size:20px; font-family: 'Cabin Sketch', cursive;">{{ movie.movie_name }}</h4>
    </p>

  </div>

</div>
