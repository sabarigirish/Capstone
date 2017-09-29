import { Meteor } from 'meteor/meteor';

Meteor.startup(() => {
    // MongoDB collection
    twitterData  = new Mongo.Collection('oneYearData');
    labels = new Mongo.Collection('label');
    if(Meteor.isServer) {
        console.log('Server is running.....');

        Meteor.publish('one_year_filtered', function(){
            return twitterData.find({}, {limit:100});
            //return twitterData.find({}, {sort: {fitnessFuncValue:-1}, limit:5});
        });

    }

});
