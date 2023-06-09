import pandas as pd
import numpy as np
from PIL import Image
from scipy import stats
import matplotlib.pyplot as plt
import os
from sklearn.metrics import r2_score


class Chroma():
    """
    Chroma is an object which application is to treat (data analysis) scanned radiochromic film data
    and turn the jpeg file into a matrix of (X,Y,Dose) shape.
    Raw data is a .jpg file.
    """
    def __init__(self,image:os.DirEntry,manual_calibration:bool=False,calibration:pd.DataFrame=None,model_type='linear',material_type='EBT-3'):
        import numpy as np
        self.image_dir = image
        self.manual_calibration = manual_calibration
        self.data = []
        self.calibration = calibration
        self.big_image = self.open_image_file()
        self.model_type = model_type
        self.rc = {'material':{'EBT-3':{'quadratic_term':0,'linear_term':0,'intercept':0,'std_bg':0}},'start_at':100}
    
    def open_image_file(self):
        try:
            big_image = Image.open(self.image_dir)
            plt.imshow(big_image)
        except:
            raise FileNotFoundError
        return big_image


    def quality_reducer(self,reduction_factor:int=5,plot_show:bool=False) -> np.array:
        full_image = self.big_image
        reduced_pattern = full_image.resize((np.array(full_image.size)/reduction_factor).astype(int))
        r_array = np.array(reduced_pattern)
        if plot_show:
                imgplot = plt.imshow(r_array, interpolation='bilinear')
        self.reduced_image = r_array
        return r_array

    #items to be filled in
    def dimension_splitter(self,start_at:int=100) -> pd.DataFrame:
            image = self.reduced_image
            x_length = np.array(image).shape[0]
            y_length = np.array(image).shape[1]
            image_array = np.array(image)
            red = []
            green = []
            blue = []
            average_channel =[]
            x_position =[]
            y_position =[]

            for x in range(start_at,x_length):
            #Converts the image into a (x,y,R,G,B) matrix
                    for y in range(y_length):
                            red.append(int(str(image_array[x,y,0])))
                            green.append(int(str(image_array[x,y,1])))
                            blue.append(int(str(image_array[x,y,2])))
                            average_channel.append(image_array[x,y,:].mean())
                            x_position.append(x)
                            y_position.append(y)

            image_matrix_data = {'x':x_position,'y':y_position,'average channel':average_channel,'red':red,'green':green,'blue':blue}

            df= pd.DataFrame(image_matrix_data)
            #generates the negative
            df['neg_red']= 255-df['red']
            df['neg_green']= 255-df['green']
            df['neg_blue']= 255-df['blue']
            
            self.data = df

            return df

    def calibrate(self,calibration_tape:np.array,dose_scale:list=[0,5,10,15,20,25,30,40,50,75,100],
                    freeze_y:int=50, iteration_range=(25,565,50),manual_input=False, manual_points:list=[]) -> pd.DataFrame:
        item_list=[]
        red_ruler = []
        green_ruler=[]
        blue_ruler=[]
        average_ruler_chanel=[]
        end = len(dose_scale)
        if manual_input == True:

                for i in manual_points:
                        print(i)
                        red_ruler.append(int(str(calibration_tape[freeze_y,i,0])))
                        green_ruler.append(int(str(calibration_tape[freeze_y,i,1])))
                        blue_ruler.append(int(str(calibration_tape[freeze_y,i,2])))
                        average_ruler_chanel.append(calibration_tape[freeze_y,i,:].mean())
                        item_list.append(i)                
                
        else:
        
                start_ = iteration_range[0]
                stop_ = iteration_range[1]
                step_ = iteration_range[2]
            
                #the array's shape is equal to (250,1280,3)
                #given the actual shape of the array the analyzed pixels on the 
                for item, i in enumerate(range(start_,stop_,step_)):
                        print(i)
                        red_ruler.append(int(str(calibration_tape[freeze_y,i,0])))
                        green_ruler.append(int(str(calibration_tape[freeze_y,i,1])))
                        blue_ruler.append(int(str(calibration_tape[freeze_y,i,2])))
                        average_ruler_chanel.append(calibration_tape[freeze_y,i,:].mean())
                        item_list.append(i)
        # green_ruler[0]=str(green_ruler[0]) # it is needed to convert this datapoint to string
        #the value mismatches the collected one
        try:
                calibration_df = pd.DataFrame({'Dose [Gy]':dose_scale[:end],'Red Intensity':red_ruler[:end],'Green Intensity':green_ruler[:end],'Blue Intensity':blue_ruler[:end],'Average':average_ruler_chanel[:end]})
        except ValueError:
                calibration_df = pd.DataFrame({'Dose [Gy]':dose_scale[:len(red_ruler[:end])],'Red Intensity':red_ruler[:end],'Green Intensity':green_ruler[:end],'Blue Intensity':blue_ruler[:end],'Average':average_ruler_chanel[:end]})

        #the following line of code is required so that the string is converted back to int
        calibration_df['Green Intensity']=calibration_df['Green Intensity'].apply(int)
        # calibration_df.plot(x='Dose [Gy]',y=['Red Intensity','Green Intensity','Blue Intensity','Average'])
        #Obtaining the negatives

        calibration_df['Green Intensity Neg'] = 255 - calibration_df['Green Intensity']
        calibration_df['Red Intensity Neg'] = 255 - calibration_df['Red Intensity'] 
        calibration_df['Blue Intensity Neg'] = 255 - calibration_df['Blue Intensity']
        calibration_df.plot(x='Dose [Gy]',y=['Red Intensity Neg','Green Intensity Neg','Blue Intensity Neg'])
        self.calibration = calibration_df
        return calibration_df

    def bg_remover(self,
                    bg_row:int=0,
                    all_channels:bool=False,
                    target_channel:str='Green Intensity Neg') -> pd.DataFrame:
            """ State of art?Please Select One channel ONLY"""
            calibration_df = self.calibration_df
            background = calibration_df.iloc[bg_row][target_channel]
            updated_info = calibration_df[target_channel] - background
            return list(updated_info),background

    # corrected_spect,bg = bg_remover(calibration_df)


    def dose_regression(self,calibration:pd.DataFrame,corrected_spect:list,bg:int,dose_threshold:int=6,model_type='linear'):
            calibration = self.calibration
            data = self.data
            x = corrected_spect[:dose_threshold]
            y = calibration['Dose [Gy]'][:dose_threshold]
            if model_type == 'linear':
                regression = stats.linregress(x,y)
                linear_term = regression.slope
                intercept = regression.intercept
                r_squared = regression.rvalue
                quadratic_term = 0
                model = lambda x_:linear_term*(x_-bg) + intercept
            elif model_type == 'quadratic':
                regression = np.polyfit(x,y,2)
                quadratic_term,linear_term,intercept = regression
                model = lambda x_:quadratic_term*(x_-bg)**2+linear_term*(x_-bg) + intercept
                model_overall = np.poly1d(regression)
                r_squared = r2_score(y,model_overall(x))

            dose = data['neg_green'].apply(model)
            self.data['Dose'] = dose
            return quadratic_term,linear_term,intercept,r_squared,dose

    def standard_regression(self):
        #use only terms that are found it the standard configuration
        data = self.data
        bg = self.material.material_type.std_bg
        source = self.material.material_type
        if self.model_type == 'linear':
                model = lambda x_:source.linear_term*(x_-bg) + source.intercept
        elif self.model_type == 'quadratic':
                model = lambda x_:source.quadratic_term*(x_-bg)**2+source.linear_term*(x_-bg) + source.intercept
        dose = data['neg_green'].apply(model)
        self.data['Dose'] = dose
        return self.data
    
    def plot_module(self):
        x_max = max(self.data.x) + 1
        y_max = max(self.data.y) + 1
        x_shape = x_max - int(self.data.x[0])
        y_shape = y_max - int(self.data.y[0])
        z = np.array(self.data.Dose).reshape(x_shape,y_shape)
        X, Y = np.meshgrid(y_shape,x_shape,sparse=False)
        fig,ax=plt.subplots(1,1)
        cp = ax.contourf(X,Y, z,corner_mask=False,cmap='gist_earth')
        fig.colorbar(cp) # Add a colorbar to a plot
        #plt.clim(0, 30)
        ax.set_title('Dose distribution for {0}'.format(self.image_dir.split('/')[-1]))
        ax.set_xlabel('Pixel X')
        ax.set_ylabel('Pixel Y')
        return plt.show()    

    def resolve(self):
        self.quality_reducer()
        self.dimension_splitter()
        self.standard_regression()
        return self.plot_module()