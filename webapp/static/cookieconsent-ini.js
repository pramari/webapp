// obtain plugin
var cc = initCookieConsent();
// https://github.com/orestbida/cookieconsent/issues/442
//
// run plugin with your configuration
cc.run({
    current_lang: "en",
    autoclear_cookies: true,                   // default: false
    page_scripts: true,                        // default: false
    mode: "opt-out", // default: 'opt-in'; value: 'opt-in' or 'opt-out'
    // delay: 0,                               // default: 0
    auto_language: "browser",  // default: null; also be 'browser' or 'document'
    // autorun: true,                          // default: true
    // force_consent: false,                   // default: false
    // hide_from_bots: false,                  // default: false
    // remove_cookie_tables: false             // default: false
    // cookie_name: 'cc_cookie',               // default: 'cc_cookie'
    // cookie_expiration: 182,                 // default: 182 (days)
    // cookie_necessary_only_expiration: 182   // default: disabled
    // cookie_domain: location.hostname,       // default: current domain
    // cookie_path: '/',                       // default: root
    // cookie_same_site: 'Lax',                // default: 'Lax'
    // use_rfc_cookie: false,                  // default: false
    // revision: 0,                            // default: 0

    onFirstAction: function(user_preferences, cookie){
        // callback triggered only once
    },


    onAccept: function (cookie) {
    /* onConsent: () => {
        if(cc.acceptedCategory('analytics')) {
            _paq.push(['setConsentGiven']);
        }*/
    },

    onChange: function (cookie, changed_preferences) {
    /* onChange: ({ changedCategories }) => {
      if(changedCategories.includes('analytics') {
        if(!cc.acceptedCategory('analytics')) {
          _paq.push(['forgetConsentGiven']);
        } else {
            _paq.push(['setConsentGiven']);
        }
      }, */
    },

    languages: {
        "en": {
            consent_modal: {
                description:
                "Hi, this website uses essential cookies to ensure its proper operation and tracking cookies to understand how you interact with it. The latter will be set only after consent. <button type='button' data-cc='c-settings' class='cc-link'>Let me choose</button>",
                primary_btn: {
                    role: "accept_all", // 'accept_selected' or 'accept_all'
                    text: "Accept all"
                },
                title: "We use cookies!",
                secondary_btn: {
                    role: "accept_necessary", // 'settings' or 'accept_necessary'
                    text: "Reject all"
                }
            },
            settings_modal: {
                title: "Cookie preferences",
                save_settings_btn: "Save settings",
                accept_all_btn: "Accept all",
                reject_all_btn: "Reject all",
                close_btn_label: "Close",
                cookie_table_headers: [
                    {col1: "Name"},
                    {col2: "Domain"},
                    {col3: "Expiration"},
                    {col4: "Description"}
                ],
                blocks: [
                    {
                        description: "We use cookies to ensure the basic functionalities of the website and to enhance your online experience. You can choose for each category to opt-in/out whenever you want. For more details relative to cookies and other sensitive data, please read the full <a href='#' class='cc-link'>privacy policy</a>.",
                        title: "Cookie usage"
                    }, {
                        description: "These cookies are essential for the proper functioning of my website. Without these cookies, the website would not work properly",
                        title: "Strictly necessary cookies",
                        toggle: {
                            enabled: true,
                            readonly: true, // categories with readonly=true are treated as "necessary cookies"
                            value: "necessary"
                        },
                        cookie_table: [{ // list of all expected cookies
                            col1: "cc_cookie", // match all cookies starting with "cc_cookie"
                            col2: ".pramari.de",
                            col3: "6 Months",
                            col4: "To remember your cookie choice",
                            is_regex: true
                        }, {
                            col1: "^_pk_id",       // all cookies starting with "_pk_id"
                            col2: ".pramari.de",
                            col3: "1 Year",
                            col4: "Pramari Session Management",
                            is_regex: true
                        }],
                    }, {
                        title: 'Performance and Analytics cookies',
                        description: 'These cookies allow the website to remember the choices you have made in the past',
                        toggle: {
                            value: "analytics",     // your cookie category
                            enabled: true,
                            readonly: false
                        },
                        cookie_table: [             // list of all expected cookies
                            {
                                col1: "^_mtm",       // match all cookies starting with "_mtm"
                                col2: "track.pramari.de",
                                col3: "2 years",
                                col4: "Product Analytics",
                                is_regex: true
                            },
                        ]
                    }, {
                        title: "Advertisement and Targeting cookies",
                        description: "These cookies collect information about how you use the website, which pages you visited and which links you clicked on. All of the data is anonymized and cannot be used to identify you. At least that is what others claim. We don't do that shit here. That's why this section is empty and disabled.",
                        toggle: {
                            value: "targeting",
                            enabled: false,
                            readonly: false
                        }
                    }, {
                        title: "More information",
                        description: "For any queries in relation to our policy on cookies and your choices, please <a class='cc-link' href='#yourcontactpage'>contact us</a>.",
                    }
                ]
            }
        }
    }
});

