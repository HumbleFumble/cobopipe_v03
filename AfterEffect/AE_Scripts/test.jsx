#include "includes/config.jsx";

function testytest(){
    var config = get_config();
    config = process_config(config);
    alert(config.project_paths.film_path)
}

testytest()