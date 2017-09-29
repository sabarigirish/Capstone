import { Template } from 'meteor/templating';

import './main.html';

twitterData = new Mongo.Collection('oneYearData');
labels = new Mongo.Collection('label');

if(Meteor.isClient){
    var count = 0;
    var answerOne = false;
    var answerTwo = false;
    var answerThree = false;
    var isComplete = false;

    console.log("Client");
    Session.set('selectedTweet', -1);

    Template.content.onCreated( function() {
        this.subscribe( 'one_year_filtered', function() {
            $( ".loader" ).delay( 1 ).fadeOut( 'slow', function() {
                $( ".loading-wrapper" ).fadeIn( 'slow' );
            });
        });
    });


    Template.content.onRendered( function() {
        $( "svg" ).delay( 1000 ).fadeIn();
    });


    Template.content.helpers( {
        'document': function () {

            if(Session.get('selectedTweet') === -1) {
                return twitterData.find().fetch()[count];
            }
            else {
                return twitterData.find().fetch()[Session.get('selectedTweet')];

            }

        },

        'backButton': function () {
            return Session.get('selectedTweet') > 0;
        },

        'completed': function () {
            if(Session.get('selectedTweet') === 3) {
                isComplete = true;
            }
            return isComplete;
        }
    });


    Template.content.events( {
        'click .next': function (event, template) {
            count += 1;
            Session.set('selectedTweet',  count);
            console.log(Session.get('selectedTweet'));
            var element = template.find('input:radio[name=myBut]:checked');
            template.find("form").reset();
            console.log($(element).val());
        },

        'click .back': function (event, template) {
            count -= 1;
            Session.set('selectedTweet',  count);
            console.log(Session.get('selectedTweet'));
        }
    });


    Template.QandA.events({

        'change .qa': function (event, template) {

            //console.log(event);
            var element1 = template.find('input:radio[name=q1]:checked');
            var element2 = template.find('input:radio[name=q2]:checked');
            var element3 = template.find('input:radio[name=q3]:checked');
            console.log("Selected options: " + $(element1).val() + " and " + $(element2).val() +
                " and " + $(element3).val());

            if($(element1).val() !== undefined) {
                answerOne = true;
            }

            if($(element2).val() !== undefined) {
                answerTwo = true;
            }

            if($(element3).val() !== undefined) {
                answerThree = true;
            }

            if(answerOne && answerTwo && answerThree) {
                var index = Session.get('selectedTweet');
                count += 1;
                var element1 = template.find('input:radio[name=q1]:checked');
                var element2 = template.find('input:radio[name=q2]:checked');
                var element3 = template.find('input:radio[name=q3]:checked');
                console.log("Selected options: " + $(element1).val() + " and " + $(element2).val() +
                    " and " + $(element3).val());

                var data = twitterData.find().fetch()[index];
                var tweetID = data['id'];
                var tweetText = data['text'];
                console.log(data);
                console.log(tweetID);
                console.log(tweetText);

                labels.insert({
                        id: tweetID,
                        label1: $(element1).val(),
                        label2: $(element2).val(),
                        label3: $(element3).val()
                    }
                );


                answerOne = false;
                answerTwo = false;
                answerThree = false;
                template.find("form").reset();
            }
            Session.set('selectedTweet',  count);
        },


    });
}




