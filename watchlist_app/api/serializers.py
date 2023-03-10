from rest_framework import serializers
from watchlist_app.models import WatchList, StreamPlateform, Review

class ReviewSerializer(serializers.ModelSerializer):
    review_user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Review
        # fields = "__all__"
        exclude = ('watchlist',)
     
    
               
class WatchListSerializer(serializers.ModelSerializer):
    # reviews = ReviewSerializer(many=True, read_only=True)
    platform = serializers.CharField(source='platform.name')    # Before without this line, output:
                                                                # 'platform' = 10
                                                                
                                                                # After output:
                                                                # 'platform' = Netflix                                  
    class Meta:
        model = WatchList
        fields = "__all__"
        
        
class StreamPlateformSerializer(serializers.ModelSerializer):
    watchlist = WatchListSerializer(many=True, read_only=True)
    
    
    class Meta:
        model = StreamPlateform
        fields = "__all__"
                     
        
        

        
        
            