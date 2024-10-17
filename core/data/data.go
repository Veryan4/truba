package data

import "embed"

//go:embed scraper_data/*
var ScraperData embed.FS

//go:embed images/*
var ImageData embed.FS
