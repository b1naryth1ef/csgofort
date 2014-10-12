vac = {}

function run(route) {
    if (route === "" || route === "/") {
        vac.run_index();
    }
    // } else if (route === "/api") {
    //     maz.run_api_docs();
    // } else if (route.lastIndexOf("/item", 0) === 0) {
    //     maz.run_item();
    // } else if (route === "/value") {
    //     maz.run_value();
    // } else if (route === "/inventory") {
    //     maz.run_inventory();
    // } else if (route === "/stats") {
    //     maz.run_stats();
    // }
}


vac.run_index = function() {
    console.log(":^)")
}