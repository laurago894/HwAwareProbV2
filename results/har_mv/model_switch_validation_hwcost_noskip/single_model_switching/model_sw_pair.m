% rain% [corrs,costss,predss,modelss]=pair_switch(alones,freq,thres,check_time)
dir_name='pareto_pruned_bits';

%% Settings
dns={'20_30','40_50','20_50','60_70','40_70','80_90','60_90','100_110','80_110','120_130','100_130','140_150','120_150','160_170','140_170'};
dns2={'20_30','40_50','20_50','60_70','40_70','80_90','60_90','100_110','80_110','120_130','100_130','140_150','120_150','160_170','140_170'};
names={'20,30','40,50','20,50','60,70','40,70','80,90','60,90','100,110','80,110','120,130','100,130','140,150','120,150','160,170','140,170'};
max_cost_final=1946000;

accs=0.7:0.1:0.9;
% accs=0.1:0.05:1;

freqs=[2,5:5:25];
% freqs=[2:1:30];
marks={'*','o','d'};
combos=[1,3;2,3;1,2];
colors_combos={'m','g','c'};
for combo=1:3
    %% Load Paretos and train data
    models_sw=csvread([dir_name '/models_switch.csv'],1,0);
    pareto_final_gen_cmi_prune=csvread(['/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/results/har_mv/pruning_gen_cmi_hwcost/' dir_name '_valid_acc.csv'],0,1);
        
    trainsdata{1}=csvread([dir_name '/res_train_gen_cmi_pt_' num2str(models_sw(3,1)-1) '.csv'],1,0);
    tedata{1}=csvread([dir_name '/res_valid_gen_cmi_pt_' num2str(models_sw(3,1)-1) '.csv'],1,0);

    trainsdata{2}=csvread([dir_name '/res_train_gen_cmi_pt_' num2str(models_sw(2,1)-1) '.csv'],1,0);
    tedata{2}=csvread([dir_name '/res_valid_gen_cmi_pt_' num2str(models_sw(2,1)-1) '.csv'],1,0);

    trainsdata{3}=csvread([dir_name '/res_train_gen_cmi_pt_' num2str(models_sw(1,1)-1) '.csv'],1,0);
    tedata{3}=csvread([dir_name '/res_valid_gen_cmi_pt_' num2str(models_sw(1,1)-1) '.csv'],1,0);


    alonestrain{1}=trainsdata{combos(combo,1)};
    alonestrain{2}=trainsdata{combos(combo,2)};
    
    %% Plot reference
%     figure(1);
    
    alones{1}=tedata{combos(combo,1)};
    alones{2}=tedata{combos(combo,2)};
    
    
    for d=1:length(dns)
%         subplot(2,2,d)
        figure(d)
        hold on; grid on;
        plot(pareto_final_gen_cmi_prune(:,2)/max_cost_final,pareto_final_gen_cmi_prune(:,1),'k.-')
        hold on;
        plot([mean(alones{1}(:,8)),mean(alones{2}(:,8))]./max_cost_final,[mean(alones{1}(:,7)),mean(alones{2}(:,7))],[colors_combos{combo} marks{combo} '--'],'LineWidth',2)
    end
    xlabel('Cost')
    ylabel('Accuracy')
    %% Extract confusion matrices and expected accuracy
    
    pdist=0:0.005:1;
    
    pd=pdist(2:end);
    
    
    for m=1:2
        
        [mattr{m},matprobtr{m},mprobstr{m}]=confusion_matrix(0:5,alonestrain{m},pdist);
        tp{m}=diag(mattr{m});
        
        for c=1:6
            t1=mprobstr{m}(c,c,:);
            tp_probs{m}(c,:)=t1;
            clear temp
            temp=mattr{m}(:,c);
            temp(c)=[];
            fp{m}(:,c)=temp;
            
            t2=mprobstr{m}(:,c,:);
            tt2=reshape(t2,6,length(pdist));
            tt2(c,:)=[];
            fp_probs{m}(c,:)=sum(tt2,1);
        end
        
    end
    
    for m=1:2
        for c=1:6
            cs_tp=cumsum(tp_probs{m}(c,:));
            cs_fp=cumsum(fp_probs{m}(c,:));
            
            expected_acc{m,c}=[pdist(2:end);(cs_tp(1:end-1))./(cs_tp(1:end-1)+cs_fp(1:end-1))];
            
            
            
        end
    end
    
    
    [a1,b1]=histc(alonestrain{1}(:,6),0:5);
    [a2,b2]=histc(alonestrain{2}(:,6),0:5);
    
    %% Extract thresholds
    for d=1:length(dns)
        main_dir=['/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/results/har_mv/model_switch_validation_hwcost_noskip/data_random_' dns{d} '/'];
%         subplot(2,2,d)
        figure(d)
        title(names{d})
        ylim([0.7,0.95])
%         xlim([0.3,0.7])
        for a=1:length(accs)
            
            acc_lim=accs(a);
            
            small_to_big=zeros(6,1); %if currently in model 1 and incoming prob <= than this threshold, go to larger model
            big_to_small=0.99*ones(6,1);%if currently in model 2 and incoming prob >= than this threshold, feel safe to go to smaller model
            
            for c=1:6
                
                %find the location in both models where they exceed expected acc.
                
                locsm1=find(expected_acc{1,c}(2,:)>=acc_lim);
                locsm2=find(expected_acc{2,c}(2,:)>=acc_lim);
                
                %For small to big
                %Find the location (in the prob distribution) where larger model is
                %guaranteed to be better. Indeed if larger model is guaranteed to be
                %better it is always worth switching to it.
                if ~isempty(locsm1) && (a1(c)./sum(a1) > (1/6)/2)
                    locs_bt=intersect(locsm2,find(expected_acc{2,c}(2,:)>expected_acc{1,c}(2,:)));
                    if locs_bt
                        temp=expected_acc{2,c}(1,locs_bt-1);
                        small_to_big(c)=temp(1);
                    else
                        if locsm1
                            small_to_big(c)=1;
                        end
                    end
                end
                
                
                %For big to small: will only do this if we know there are instances
                %if smaller model is better and bigger model AND smaller has reached
                %its highest exp.acc.
                if locsm1 %if smaller actually surpasses the accuracy bound
                    
                    %find where is smaller model reaching its highest exp. acc.
                    max_acc1_loc=find(expected_acc{1,c}(2,:)==max(expected_acc{1,c}(2,:)));
                    %if it is better than larger at that location, then we can switch
                    %from larger to smaller at that location
                    if sum(expected_acc{2,c}(2,max_acc1_loc)>max(expected_acc{1,c}(2,:)))==0
                        big_to_small(c)=expected_acc{1,c}(1,max_acc1_loc(1)-1);
                    end
                end
                
                
            end
            
            thres=small_to_big;
            
            % markers={'x-','+-','o-'};
            %
            %
            % figure();
            % for c=1:6
            %     subplot(3,2,c)
            %     for m=1:2
            %         grid on; hold on;
            %         plot(expected_acc{m,c}(1,:),expected_acc{m,c}(2,:),markers{m});
            %     end
            %     ylim([0.5,1])
            %     plot(pd,acc_lim*ones(length(pd),1),'k--')
            %     legend('Model 1','Model 2','Limit','Location','Southeast')
            %     title(['Predictions of class ' num2str(c)])
            % end
            
            
            
            
            
            
            
            %% Switching
            for f=1:length(freqs)
                freq=freqs(f);
                for ct=[0,1]
                    all_costs=[];
                    all_accs=[];
                    for ii=1:5
                        %% Load test datasets
                        
                        
                        seq=csvread(['/users/micas/lgalinde/Documents/code_2019/HwAwareProbV2/datasets/har_mv/har_mv_fold0/har_mv_order_random_' dns2{d} '_' num2str(ii) '.valid.seq.csv']);
                        alones{1}=tedata{combos(combo,1)}(seq,:);
                        alones{2}=tedata{combos(combo,2)}(seq,:);
                        
                        [corrs,costss,predss,modelss]=pair_switch(alones,freq,thres,ct);
                        all_costs=[all_costs,mean(costss)];
                        all_accs=[all_accs,mean(corrs)];
                    end
                    if ct==0
                        marker=[colors_combos{combo} 'o'];
                    elseif ct==1
                        marker=[colors_combos{combo} 'p'];
                    end
                    hold on;
                    plot(mean(all_costs)./max_cost_final,mean(all_accs),marker)
                end
            end
        end
    end
end