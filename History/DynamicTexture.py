
from joblib import dump, load
from LDP import LDP_TOP
import numpy as np
import cv2
import numpy as np


class dynamicTexture:
    def __init__(self, dataset_version, model_version, path):
        """
        Initializes an instance of the dynamicTexture class.

        :param dataset_version: The version of the dataset ('cf23' or 'cf40').
        :param model_version: The version of the model ('binary' or 'multi').
        :param path: The path to the model files.
        """

        assert dataset_version == 'cf23' or dataset_version == 'cf40', "dataset_version is not equal to 'cf23' or 'cf40'"
        assert model_version == 'binary' or model_version == 'multi', "model_version is not equal to 'binary' or 'multi'"

        self.dataset_version = dataset_version
        self.model_version = model_version

        if (dataset_version == 'cf23'):
            if (model_version == 'binary'):
                self.linear_deepfakes = load(
                    path + 'cf23/Linear-Deepfakes.joblib')
                self.linear_face2face = load(
                    path + 'cf23/Linear-Face2Face.joblib')
                self.linear_faceswap = load(
                    path + 'cf23/Linear-FaceSwap.joblib')
                self.linear_neuraltextures = load(
                    path + 'cf23/Linear-NeuralTextures.joblib')

            elif (model_version == 'multi'):
                self.linear_svm = load(
                    path + 'cf23/Linear-SVM.joblib')

        elif (dataset_version == 'cf40'):
            self.linear_deepfakes = load(
                path + 'cf40/Linear-Deepfakes.joblib')
            # self.linear_face2face = load(
            #    path + 'cf40/Linear-Face2Face.joblib')
            self.linear_faceswap = load(
                path + 'cf40/Linear-FaceSwap.joblib')
            # self.linear_neuraltextures = load(
            #  path + 'cf40/Linear-NeuralTextures.joblib')



    def predict(self, input_gray_frames, frame_rate):
        """
        Predicts the class labels for input frames.

        :param input_gray_frames: The input grayscale frames.
        :param frame_rate: The frame rate for partitioning the frames.
        :return: The predicted class labels.
        """

        resized_frames = []
        for input_gray_frame in input_gray_frames:
            resized_frame = cv2.resize(input_gray_frame, (128, 128))
            resized_frames.append(resized_frame)

        frames_partitions = [resized_frames[i:i+(frame_rate*3)]
                             for i in range(0, len(resized_frames), (frame_rate*3))]

        list_of_test_LDP = []
        for frame_partition in frames_partitions:
            frames_ldp = LDP_TOP(np.array(frame_partition).astype(np.float64))
            list_of_test_LDP.append(frames_ldp)

        if (self.dataset_version == 'cf23'):
            if (self.model_version == 'binary'):
                return self.binary_predictor(list_of_test_LDP)
            elif (self.model_version == 'multi'):
                return self.multi_predictor(list_of_test_LDP)

        elif (self.dataset_version == 'cf40'):
            return self.binary_predictor(list_of_test_LDP)

    def multi_predictor(self, list_of_test_LDP):
        """
        Makes predictions using the multi-class model.

        :param list_of_test_LDP: The list of LDP features for test partitions.
        :return: The predicted class labels.
        """
        y_pred = self.linear_svm.predict(list_of_test_LDP)
        return y_pred

    def binary_predictor(self, list_of_test_LDP):
        """
        Makes predictions using the binary models.

        :param list_of_test_LDP: The list of LDP features for test partitions.
        :return: The predicted class labels.
        """
        df_pred = self.linear_deepfakes.predict(list_of_test_LDP)
        if (self.dataset_version == 'cf23'):
            f2f_pred = self.linear_face2face.predict(list_of_test_LDP)
        fsw_pred = self.linear_faceswap.predict(list_of_test_LDP)
        if (self.dataset_version == 'cf23'):
            nt_pred = self.linear_neuraltextures.predict(list_of_test_LDP)
            
        if (self.dataset_version == 'cf23'):
            return df_pred, f2f_pred, fsw_pred, nt_pred
        elif (self.dataset_version == 'cf40'):
            return df_pred,  fsw_pred
