pref("services.sync.serverURL", "https://komodo-sync.activestate.com/");
pref("services.sync.storageAPI", "1.0");
pref("services.sync.userURL", "user/");
pref("services.sync.miscURL", "misc/");
// FIXME fix those:
pref("services.sync.termsURL", "https://services.mozilla.com/tos/");
pref("services.sync.privacyURL", "https://services.mozilla.com/privacy-policy/");
pref("services.sync.statusURL", "https://services.mozilla.com/status/");
pref("services.sync.syncKeyHelpURL", "https://services.mozilla.com/help/synckey");

pref("services.sync.lastversion", "firstrun");
pref("services.sync.autoconnect", false);
//pref("services.sync.autoconnectDelay", 3);

pref("services.sync.engine.apicatalogs", true);
pref("services.sync.engine.keybindings", true);
pref("services.sync.engine.kopasswords", true);
pref("services.sync.engine.koprefs", true);
pref("services.sync.engine.projecttemplates", true);
pref("services.sync.engine.schemes", true);
pref("services.sync.engine.templates", true);
pref("services.sync.engine.tools", true);

pref("services.sync.engine.bookmarks", false);
pref("services.sync.engine.history", false);
pref("services.sync.engine.passwords", false);
pref("services.sync.engine.prefs", false);
pref("services.sync.engine.tabs", false);

// Not really using those:
pref("services.sync.jpake.serverURL", "https://setup.services.mozilla.com/");
pref("services.sync.jpake.pollInterval", 1000);
pref("services.sync.jpake.firstMsgMaxTries", 300);
pref("services.sync.jpake.maxTries", 10);

pref("services.sync.log.appender.console", "Warn");
pref("services.sync.log.appender.dump", "Error");
pref("services.sync.log.appender.debugLog", "Trace");
pref("services.sync.log.appender.debugLog.enabled", false);
pref("services.sync.log.rootLogger", "Debug");
pref("services.sync.log.logger.service.main", "Debug");
pref("services.sync.log.logger.authenticator", "Debug");
pref("services.sync.log.logger.network.resources", "Debug");
pref("services.sync.log.logger.service.jpakeclient", "Debug");
pref("services.sync.log.logger.engine.bookmarks", "Debug");
pref("services.sync.log.logger.engine.clients", "Debug");
pref("services.sync.log.logger.engine.forms", "Debug");
pref("services.sync.log.logger.engine.history", "Debug");
pref("services.sync.log.logger.engine.passwords", "Debug");
pref("services.sync.log.logger.engine.prefs", "Debug");
pref("services.sync.log.logger.engine.tabs", "Debug");
pref("services.sync.log.cryptoDebug", false);


// Preferences that the Prefs Engine should sync:
pref("services.sync.koprefs.sync.show_start_page", true);
pref("services.sync.koprefs.sync.start_page_quick_links_box_closed", true);
pref("services.sync.koprefs.sync.start_page_tip_box_closed", true);
pref("services.sync.koprefs.sync.start_page_landing_box_closed", true);

pref("services.sync.koprefs.sync.mruProjectSize", true);
pref("services.sync.koprefs.sync.mruFileSize", true);
pref("services.sync.koprefs.sync.mruTemplateSize", true);

pref("services.sync.koprefs.sync.showMatchingTagsOnClick", true);
pref("services.sync.koprefs.sync.showMatchingTags_constrainSearchInViewPort", true);
pref("services.sync.koprefs.sync.showMatchingTags_clearInterval", true);

pref("services.sync.koprefs.sync.ui.tabs.sidepanes.left.layout", true);
pref("services.sync.koprefs.sync.ui.tabs.sidepanes.right.layout", true);
pref("services.sync.koprefs.sync.ui.tabs.sidepanes.bottom.layout", true);

pref("services.sync.koprefs.sync.debuggerHoverValue", true);

pref("services.sync.koprefs.sync.lintJavaScriptEnableWarnings", true);
pref("services.sync.koprefs.sync.lintJavaScriptEnableStrict", true);

pref("services.sync.koprefs.sync.tidy_errorlevel", true);
pref("services.sync.koprefs.sync.tidy_accessibility", true);

pref("services.sync.koprefs.sync.httpInspector_enabledAtStartup", true);
pref("services.sync.koprefs.sync.httpInspector_listenPort", true);
pref("services.sync.koprefs.sync.httpInspector_acceptLocalConnectionsOnly", true);
pref("services.sync.koprefs.sync.httpInspector_proxyForwardingEnabled", true);
pref("services.sync.koprefs.sync.httpInspector_proxyForwardingAddress", true);


pref("services.sync.koprefs.sync.editSmartCutCopyWithoutSelection", true);
pref("services.sync.koprefs.sync.editTabCompletes", true);

pref("services.sync.koprefs.sync.fastopen_enable_go_tool", true);
pref("services.sync.koprefs.sync.fastopen_enable_open_views_gatherer", true);
pref("services.sync.koprefs.sync.fastopen_enable_history_gatherer", true);
pref("services.sync.koprefs.sync.fastopen_enable_cwd_gatherer", true);
pref("services.sync.koprefs.sync.fastopen_enable_project_gatherer", true);
pref("services.sync.koprefs.sync.fastopen_history_num_entries", true);