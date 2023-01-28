function insertKeywords(language) {
    const storiesCursor = db.Story.find({language})

    const keywordsSet = new Set()

    while (storiesCursor.hasNext()) {
        const story = storiesCursor.next()
        story.keywords.forEach(word => keywordsSet.add(word.toLowerCase()))
    }

    const keywords = [...keywordsSet].map(text => ({text, language}))
    db.Keyword.insertMany(keywords, {ordered: false})

    console.log(`Finished inserting ${language} keywords`)
}

insertKeywords("en")
insertKeywords("fr")
