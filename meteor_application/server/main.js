import { Meteor } from 'meteor/meteor';

Meteor.startup(() => {
    // MongoDB collection
    twitterData  = new Mongo.Collection('oneYearData');
    labels = new Mongo.Collection('label');
    workers = new Mongo.Collection('worker');
    hits = new Mongo.Collection('hit');
    activeTweets = new Mongo.Collection('activeTweet');
    if(Meteor.isServer) {
        console.log('Server is running.....');

        Meteor.publish('data', function(){
            return activeTweets.find({}, {sort: {fitnessFuncValue:1}});
            //return twitterData.find({}, {sort: {fitnessFuncValue:-1}, limit:5});
        });

    }

});
