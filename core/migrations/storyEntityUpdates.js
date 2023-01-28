const storiesBatchSize = 10000
let storiesBatch = []

const storiesCursor = db.Story.find({})

while (storiesCursor.hasNext()) {
    const story = storiesCursor.next()

    const storyUpdate = {
        updateOne : {
            filter: { _id: story._id},
            update: {
                $set: {
                    entities: story.entity_links.map(link => ({link, frequency: 0})),
                    keywords: story.keywords.map(text => ({text: text.toLowerCase(), frequency: 0}))
                },
                $unset: {
                    entity_links: null
                }
            }
        }
    }

    storiesBatch.push(storyUpdate)

    if (storiesBatch.length === storiesBatchSize){
        console.log(`Updating ${storiesBatch.length} stories`) 
        db.Story.bulkWrite(storiesBatch)
        storiesBatch = []
    }
}

if (storiesBatch.length > 0){
    console.log(`Updating ${storiesBatch.length} stories`) 
    db.Story.bulkWrite(storiesBatch)
}

console.log(`Finished updating stories`)