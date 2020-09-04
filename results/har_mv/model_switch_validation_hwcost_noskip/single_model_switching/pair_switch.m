function [corrs,costss,predss,modelss]=pair_switch(alones,freq,thres,check_time)

if check_time==1
    ct=0;
elseif check_time==0
    ct=-1; 
end

mod=1;
checks=zeros(length(alones{1}),1);
counter=0;
     
     
for ss=1:length(alones{1})
    
    pred=alones{mod}(ss,6);
    prob=alones{mod}(ss,5);
    corrs(ss)=alones{mod}(ss,7);
    costss(ss)=alones{mod}(ss,8);
    predss(ss)=pred;
    modelss(ss)=mod;
    
    if ss>freq+1
        nd=sum(diff(predss(end-freq-1:end))~=0);
        if counter==freq
            if nd>ct
                checks(ss)=1;
                counter=0;
                if mod==1
                    if prob>thres(pred+1)
                        mod=mod+1;
                    end
                elseif mod==2
                    if prob<=thres(pred+1)
                        mod=mod-1;
                    end
                end
            elseif nd==ct
                mod=1;
            end
        else
            counter=counter+1;
        end
    end
end