function search_2() {
    // Declare variables
    var input, filter, ul, li, a, i, txtValue, any_resu;
    input = document.getElementById('search-toggle');
    filter = input.value.toUpperCase();
    posts = document.getElementById('all')
    container1s = document.getElementsByClassName('post-container-1')
    container2s = document.getElementsByClassName('post-container-2')
    // Loop through all list items, and hide those who don't match the search query
    for (i = 0; i < container1s.length; i++) {
      post = container1s[i]
      container2 = post.getElementsByClassName('post-container-2')[0]
      category = (container2.getElementsByTagName('h2'))[0]
      title = (container2.getElementsByTagName('h1'))[0]
      tags = (container2.getElementsByTagName('h3'))
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
      if (display == false){
        post.style.opacity = 0;
        post.style.display = 'none';
      }
      else{
        post.style.opacity = 100;
        post.style.display = 'block';
      }
    };
  };