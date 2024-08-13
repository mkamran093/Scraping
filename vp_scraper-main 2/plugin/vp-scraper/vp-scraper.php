<?php
/*
Plugin Name: VP Scraper
Description: A plugin for scraping and importing products from vista print
Version: 1.0
Author: Eyosiyas Mekbib
License: GPL2
*/

function vpscraper_plugin_add_menu() {
    add_menu_page(
        'VP Scraper App',            // Page title
        'VP Scraper',                // Menu title
        'manage_options',            // Capability
        'vpscraper-plugin',          // Menu slug
        'vpscraper_plugin_render_page', // Callback function
        'dashicons-admin-generic',   // Icon
        6                            // Position
    );
}
add_action('admin_menu', 'vpscraper_plugin_add_menu');

// Render the admin page
function vpscraper_plugin_render_page() {
    // Replace 'http://localhost:3000' with the actual URL of your Next.js application
    echo '<div class="wrap"><h2>VP Scraper App</h2>';
    echo '<iframe src="http://localhost:3000" style="width:100%;height:800px;border:none;"></iframe>';
    echo '</div>';
}
