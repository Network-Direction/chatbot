# LogInsight Change Log
## v0.6 (11-01-2023)
### Added
    Added headers in the config.yaml file for authentication
    Added authentication into the plugin class

### Changed
    Inherited the plugin template class to simplify the plugin

### Fixed
    Fixed a bug where webhooks could not be received

### Caveats
    LogInsight sends the webhook authentication in CLEARTEXT
      This is not something that can be changed on this end, it is their product
