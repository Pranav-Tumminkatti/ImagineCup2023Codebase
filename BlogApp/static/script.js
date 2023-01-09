function search() {
    // Declare variables
    console.log('script called')
    var input, filter, ul, li, a, i, txtValue, any_resu;
    input = document.getElementById('search-toggle');
    filter = input.value.toUpperCase();
    posts = document.getElementById('all')
    this_page_blogs = document.getElementById('this_page_blogs')
    all_blogs = document.getElementById('all_blogs')
    articles = all_blogs.getElementsByTagName('article')
    target = document.getElementById('no_results')
    // Loop through all list items, and hide those who don't match the search query
    got_blog=true
    if(filter==""){
      this_page_blogs.style.display='block';
      all_blogs.style.display='none';
      target.style.display = 'none'
    }
    else{
      this_page_blogs.style.display='none';
      all_blogs.style.display='block';
    
    for (i = 0; i < articles.length; i++) {
      div  = (articles[i].getElementsByTagName('div'))[0]
      post = articles[i]
      console.log(post)
      category = (div.getElementsByTagName('h2'))[0]
      title = (div.getElementsByTagName('h1'))[0]
      author = (div.getElementsByTagName('h3'))[0]
      tags = (div.getElementsByTagName('h4'))
      display = false
      for(j = 0; j < tags.length; j++){
        currtag = tags[j]
        txtValue = currtag.textContent || currtag.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
        display = true
        }
      }
      txtValue = category.textContent || category.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        display = true
      }
      txtValue = title.textContent || title.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        display = true
      }
      txtValue = author.textContent || author.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        display = true
      }
      if (display == false){
        post.style.display = 'none';
      }
      else{
        post.style.display = 'block';
        got_blog=false
      }
    };
    if(got_blog==true){
      target.style.display = 'block';
      all_blogs.style.display='none'
    }
    else{
      target.style.display = 'none';
      all_blogs.style.display='block';
    }
    }
  };